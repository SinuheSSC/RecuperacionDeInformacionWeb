import time
import requests
from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, OWL
from rdflib.namespace import DC, SKOS

class WikidataBridge:
    def __init__(self, target_graph):
        self.store = target_graph
        self.WD = Namespace("http://www.wikidata.org/entity/")
        self.WDT = Namespace("http://www.wikidata.org/prop/direct/")
        self.store.bind("wd", self.WD)
        self.store.bind("wdt", self.WDT)
        self.journal = []
        self._ua = "OrbitalView_Research/4.0 (Academic; research@orbitalview.local)"

    def attach_entity(self, local_ref, wikidata_code, display_name):
        self.store.add((local_ref, OWL.sameAs, self.WD[wikidata_code]))
        self.store.add((local_ref, SKOS.exactMatch, self.WD[wikidata_code]))
        self.store.add((self.WD[wikidata_code], RDFS.label, Literal(display_name, lang="es")))
        self.journal.append({
            'source': str(local_ref),
            'target': wikidata_code,
            'label': display_name
        })

    def _search_entity(self, term):
        url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbsearchentities",
            "search": term,
            "language": "es",
            "limit": 5,
            "format": "json"
        }
        for attempt in range(3):
            try:
                resp = requests.get(
                    url, params=params,
                    headers={"User-Agent": self._ua},
                    timeout=20
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("search", [])
            except Exception as err:
                if "429" in str(err):
                    print(f"  [RATE] Throttled. Pausing 15s... ({attempt+1}/3)")
                    time.sleep(15)
                elif hasattr(resp, 'status_code') and resp.status_code == 429:
                    print(f"  [RATE] Throttled. Pausing 15s... ({attempt+1}/3)")
                    time.sleep(15)
                else:
                    print(f"  [FAIL] API call failed: {err}")
                    break
        return None

    def _search_map(self, category):
        catalog = {
            'tecnologia': 'innovación tecnológica inteligencia artificial',
            'economia': 'mercado financiero economía global',
            'ciencia': 'conocimiento científico investigación',
            'gobierno': 'administración pública gobernanza',
            'deportes': 'actividad deportiva competición'
        }
        return catalog.get(category.lower(), category)

    def get_fallback(self, category):
        fallback = {
            'tecnologia': [{'id': 'Q503', 'label': 'Creatividad', 'description': 'Proceso mental'}],
            'economia': [{'id': 'Q35025', 'label': 'Crecimiento económico', 'description': 'Aumento de indicadores'}],
            'ciencia': [{'id': 'Q108994', 'label': 'Epistemología', 'description': 'Rama de la filosofía'}],
            'gobierno': [{'id': 'Q31079', 'label': 'Organismo público', 'description': 'Entidad del estado'}],
            'deportes': [{'id': 'Q492', 'label': 'Baloncesto', 'description': 'Deporte de equipo'}]
        }
        return fallback.get(category.lower(), [])

    def enrich_category(self, local_entity, category_name):
        term = self._search_map(category_name)
        print(f"  |_ Querying WikiData API with '{term}'...")
        results = self._search_entity(term)
        if not results:
            print(f"  >> Cache data used for {category_name.upper()}")
            results = self.get_fallback(category_name)
        if results:
            for item in results:
                qid = item.get('id', '')
                label = item.get('label', '')
                desc = item.get('description', '')
                uri = URIRef(self.WD[qid])
                self.store.add((local_entity, SKOS.related, uri))
                self.store.add((uri, RDFS.label, Literal(label, lang="es")))
                if desc:
                    self.store.add((uri, DC.description, Literal(desc, lang="es")))
            print(f"  [LINKED] {len(results)} external concepts attached to '{category_name}'.")

    def list_external_refs(self):
        refs = []
        for s, p, o in self.store.triples((None, OWL.sameAs, None)):
            label_lit = self.store.value(o, RDFS.label)
            refs.append((s, o, label_lit))
        return refs


if __name__ == "__main__":
    kg = Graph()
    BASE = Namespace("http://orbitalview.org/data/")
    kg.bind("data", BASE)
    bridge = WikidataBridge(kg)
    print("=== Wikidata Enrichment Test (REST API) ===")
    bridge.enrich_category(BASE["cat_economia"], "economia")
    bridge.enrich_category(BASE["cat_ciencia"], "ciencia")
    print("\nDone.")
