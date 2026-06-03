import json
import os
from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, OWL, XSD
from rdflib.namespace import DC, SKOS
from pyshacl import validate

PROJECT_ROOT = "E:/Mi_Usuario/Documents/Proyecto1_RW_SSC/Proyecto_Final_ref/SIMANW"

class GraphAssembler:
    def __init__(self):
        self.source = f"{PROJECT_ROOT}/storage/news_corpus.json"
        self.ttl_output = f"{PROJECT_ROOT}/exports/graph.ttl"
        self.rdf_output = f"{PROJECT_ROOT}/exports/graph.rdf"
        self.jsonld_output = f"{PROJECT_ROOT}/exports/sample.jsonld"
        self.graph = Graph()
        self.ONTO = Namespace("http://data.orbitalview.org/ontology/")
        self.DATA = Namespace("http://data.orbitalview.org/instance/")
        self.WD = Namespace("http://www.wikidata.org/entity/")
        self.graph.bind("onto", self.ONTO)
        self.graph.bind("data", self.DATA)
        self.graph.bind("wd", self.WD)
        self.graph.bind("owl", OWL)
        self.graph.bind("skos", SKOS)
        self.graph.bind("dc", DC)

    def construct(self):
        print("[BUILD] Constructing knowledge graph...")
        if not os.path.exists(self.source):
            print(f"[ABORT] Corpus missing: {self.source}")
            return False
        with open(self.source, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        batch = articles[:30]
        wd_mapping = {
            "tecnologia": "Q210167", "economia": "Q3958441",
            "politica": "Q11216639", "ciencia": "Q11005", "deportes": "Q159445"
        }
        for idx, entry in enumerate(batch):
            art = URIRef(self.DATA[f"news_{idx}"])
            author_raw = entry.get('author', 'Unknown').replace(" ", "_").replace('"', '')
            author = URIRef(self.DATA[f"person_{author_raw}"])
            cat_raw = entry.get('topic', 'general').lower()
            cat = URIRef(self.DATA[f"section_{cat_raw}"])
            self.graph.add((art, RDF.type, self.ONTO.NewsArticle))
            self.graph.add((art, self.ONTO.headline, Literal(entry.get('headline', ''), datatype=XSD.string)))
            self.graph.add((art, self.ONTO.content, Literal(entry.get('body', ''), datatype=XSD.string)))
            self.graph.add((art, self.ONTO.sourceURL, URIRef(entry.get('url', 'http://unknown.org'))))
            self.graph.add((art, self.ONTO.publishDate, Literal(entry.get('date', ''), datatype=XSD.string)))
            self.graph.add((author, RDF.type, self.ONTO.Person))
            self.graph.add((author, RDFS.label, Literal(entry.get('author', 'Unknown'), datatype=XSD.string)))
            self.graph.add((art, self.ONTO.writtenBy, author))
            self.graph.add((cat, RDF.type, self.ONTO.Section))
            self.graph.add((cat, RDFS.label, Literal(cat_raw, datatype=XSD.string)))
            self.graph.add((art, self.ONTO.assignedTo, cat))
            if cat_raw in wd_mapping:
                wd_uri = URIRef(self.WD[wd_mapping[cat_raw]])
                self.graph.add((cat, OWL.sameAs, wd_uri))
                self.graph.add((wd_uri, RDFS.label, Literal(cat_raw, lang="es")))
        print(f"[READY] {len(self.graph)} RDF statements generated.")
        return True

    def query_insights(self):
        print("\n[QUERY] Executing SPARQL analytics...")
        q1 = """
        PREFIX onto: <http://data.orbitalview.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?category (COUNT(*) AS ?volume)
        WHERE { ?doc onto:assignedTo ?group . ?group rdfs:label ?category . }
        GROUP BY ?category ORDER BY DESC(?volume)
        """
        q2 = """
        PREFIX onto: <http://data.orbitalview.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?name ?title
        WHERE {
            ?news onto:writtenBy ?writer ; onto:headline ?title .
            ?writer rdfs:label ?name .
            FILTER(?name != "Unknown")
        } LIMIT 10
        """
        q3 = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?source ?target
        WHERE { ?source owl:sameAs ?target . }
        ORDER BY ?source
        """
        r1 = [{"section": str(r[0]), "articles": str(r[1])} for r in self.graph.query(q1)]
        r2 = [{"author": str(r[0]), "title": str(r[1])[:60] + "..."} for r in self.graph.query(q2)]
        r3 = [{"local": str(r[0]).split('/')[-1], "wikidata": str(r[1])} for r in self.graph.query(q3)]
        return r1, r2, r3

    def validate(self):
        print("\n[VALIDATE] Running SHACL constraints...")
        shapes = Graph()
        constraints = """
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        @prefix onto: <http://data.orbitalview.org/ontology/> .
        onto:ContentShape a sh:NodeShape ;
            sh:targetClass onto:NewsArticle ;
            sh:property [ sh:path onto:headline ; sh:datatype xsd:string ; sh:minCount 1 ; sh:maxCount 1 ; ] ;
            sh:property [ sh:path onto:sourceURL ; sh:nodeKind sh:IRI ; sh:minCount 1 ; sh:maxCount 1 ; ] .
        """
        shapes.parse(data=constraints, format="turtle")
        conforms, _, _ = validate(data_graph=self.graph, shshapes_graph=shapes, inference='rdfs')
        return conforms

    def serialize(self):
        os.makedirs(os.path.dirname(self.ttl_output), exist_ok=True)
        self.graph.serialize(destination=self.ttl_output, format="turtle")
        self.graph.serialize(destination=self.rdf_output, format="xml")
        sample = {
            "@context": {
                "onto": "http://data.orbitalview.org/ontology/",
                "data": "http://data.orbitalview.org/instance/",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "title": {"@id": "onto:headline", "@type": "xsd:string"},
                "url": {"@id": "onto:sourceURL", "@type": "@id"},
                "author": {"@id": "onto:writtenBy", "@type": "@id"}
            },
            "@id": "data:news_sample",
            "@type": "onto:NewsArticle",
            "title": "Lanzamiento del telescopio espacial James Webb detecta atmosfera en exoplaneta",
            "url": "https://www.nasa.gov/webb/exoplanet-atmosphere-discovery",
            "author": "data:person_Carlos_Mendez"
        }
        with open(self.jsonld_output, 'w', encoding='utf-8') as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
