# Actividad previa Web Semántica
**Alumno:** Sinuhe Sánchez Contreras  
**Materia:** Recuperación de Información en la Web


## Mision 0: Calentamiento (investigación breve, 15 min)

* 1. Diferencia entre página web de museo y dataset
Una página web orientada a humanos mezcla datos con diseño, tipografías y maquetación (HTML/CSS) para que sea visualmente atractiva; una máquina no puede "entender" de forma nativa qué fragmento es el horario y cuál es la dirección sin un algoritmo de raspado (scraping) propenso a fallas. En contraste, un dataset estructurado (como un CSV o JSON) aísla los hechos crudos en campos definidos por claves explícitas (ej. "latitud": 19.4326), permitiendo que cualquier software procese, filtre y compare la información de forma inmediata y sin ambigüedades. 

* 2. Significado de que un dato esté «enlazado» (Linked Data)
Que un dato esté "enlazado" significa que no solo está estructurado en la web, sino que utiliza identificadores globales únicos (URIs) para nombrar sus elementos y relaciones, conectándose explícitamente con fuentes de datos externas. Siguiendo las reglas de Tim Berners-Lee, implica que si un usuario o máquina sigue una URI (como un enlace web), encontrará más datos útiles y relaciones tipadas utilizando estándares compartidos (RDF). Convierte islas de datos aisladas en una gran red global de conocimiento interconectado.

* 3. Observación del Wikidata Query Service
Al ejecutar una consulta de demostración, el resultado visual inicial se presenta en forma de tabla con filas y columnas (muy similar al resultado de una consulta SQL convencional). Sin embargo, la gran diferencia es que las celdas no contienen texto plano inerte, sino hipervínculos a entidades globales (URIs) de Wikidata (como wd:Q90 para París). Al hacer clic en ellas, te redirigen a un grafo de conocimiento interactivo, demostrando que detrás de esa "tabla" temporal hay una red interconectada de nodos y aristas, y no una base de datos relacional tradicional y rígida.


## Misión 1: Extracción manual de «triples» desde HTML y JSON

### Triples extraídos del HTML (html_informe)
1. `("ex:alicia", "tieneNombre", "Alicia García")`
2. `("ex:alicia", "tieneRol", "Profesora de Matemáticas en la UNAM")`
3. `("ex:alicia", "conoce", "ex:bob")`
4. `("ex:bob", "tieneNombre", "Bob Martínez")`
5. `("ex:alicia", "coautorDe", "ex:articulo_redes")`
6. `("ex:bob", "coautorDe", "ex:articulo_redes")`
7. `("ex:articulo_redes", "titulo", "Redes y Grafos")`

### Triples extraídos del JSON (json_biblioteca)
1. `("ex:libro42", "titulo", "Introducción a la Web Semántica")`
2. `("ex:libro42", "tieneAutor", "Alicia García")`
3. `("ex:libro42", "tieneAutor", "Bob Martínez")`
4. `("ex:libro42", "publicadoEn", 2019)`
5. `("ex:libro42", "isbn", "978-3-030-00000-0")`

### El problema de la unificación de identidades
* **Triples en conflicto:**
  * HTML: `("ex:alicia", "tieneNombre", "Alicia García")`
  * JSON: `("ex:libro42", "tieneAutor", "Alicia García")`

* **Explicación:** Si la máquina procesa ambos archivos de forma aislada, interpretará que el autor del libro en el JSON es simplemente una cadena de texto plano (`"Alicia García"`), mientras que en el HTML es una entidad abstracta (`ex:alicia`). Para el sistema, el texto plano no tiene identidad única; no puede deducir de forma segura si la autora del libro es la misma profesora de la UNAM o un homónimo. Sin un identificador global común (como una URI compartida), los datos se quedan aislados en silos independientes.

### Código de validación completado
```python
triples_html = [
    ("ex:alicia", "tieneNombre", "Alicia García"),
    ("ex:alicia", "tieneRol", "Profesora de Matemáticas en la UNAM"),
    ("ex:alicia", "conoce", "ex:bob"),
    ("ex:alicia", "coautorDe", "ex:articulo_redes")
]

triples_json = [
    ("ex:libro42", "titulo", "Introducción a la Web Semántica"),
    ("ex:libro42", "tieneAutor", "Alicia García"),
    ("ex:libro42", "publicadoEn", 2019)
]

def cubre(triples, predicados_esperados):
    preds = {p for _, p, _ in triples}
    faltan = set(predicados_esperados) - preds
    print("Predicados presentes:", sorted(preds))
    print("Faltan:", sorted(faltan) if faltan else "ninguno")

print("--- Validación HTML ---")
cubre(triples_html, {"tieneNombre", "tieneRol", "conoce", "coautorDe"})

print("\n--- Validación JSON ---")
cubre(triples_json, {"titulo", "tieneAutor", "publicadoEn"})
```

* **Pregunta de cierre** No, la extracción manual dejaría de ser válida. Si el código encargado de extraer los datos (un scraper) depende de buscar etiquetas estructurales específicas como un <h1>, cualquier cambio estético o de diseño rompería el flujo. Esto demuestra el riesgo de mezclar los datos con la presentación: el HTML fue diseñado para indicar al navegador cómo mostrar el contenido visualmente, no para definir qué significa. La Web Semántica busca precisamente separar el significado puro (los datos en triples) de su representación gráfica.


## Misión 2 — URIs, sinónimos y el problema «París»

### Tabla de Identificadores Globales (Alineación de `fuente_a`)

| nombre_en_texto | URI_propuesta | tipo_entidad |
| :--- | :--- | :--- |
| París | `http://geo.example/city/paris` | Ciudad / Capital |
| París Hilton | `http://people.example/paris_hilton` | Persona |
| FR | `http://geo.example/country/fr` | País |

### Triples de alineación entre fuentes
Para mapear y fusionar los datos locales de la `fuente_a` con las URIs ya normalizadas de la `fuente_b`, utilizamos el predicado estándar `owl:sameAs` (que declara identidad exacta entre dos recursos):

1. `(http://geo.example/city/paris, owl:sameAs, wd:Q90)`
2. `(http://geo.example/country/fr, owl:sameAs, wd:Q142)`
3. `(http://people.example/paris_hilton, owl:sameAs, wd:Q47899)`

### Limitación de la búsqueda por palabras clave vs URIs
La búsqueda literal por palabras clave falla ante la **polisemia** (el término "París" puede referirse a una ciudad o a una celebridad) y la **sinonimia** (las cadenas "FR" y "Francia" apuntan al mismo objeto real), mezclando o perdiendo resultados. Una URI aporta un identificador único y global que desambigua el concepto de su representación textual. Esto permite que las máquinas entiendan con total certeza a qué entidad exacta nos referimos, independientemente del idioma o del contexto en el que se escriba.

### Código de simulación completado (Opcional)
```python
uri_labels = {
    "[http://geo.example/city/paris](http://geo.example/city/paris)": "París (ciudad)",
    "[http://people.example/paris_hilton](http://people.example/paris_hilton)": "Paris Hilton",
    "[http://geo.example/country/fr](http://geo.example/country/fr)": "Francia",
}

same_as = {
    "París": "[http://geo.example/city/paris](http://geo.example/city/paris)",
    "Francia": "[http://geo.example/country/fr](http://geo.example/country/fr)",
}

def resolver(nombre_o_uri):
    return uri_labels.get(nombre_o_uri, uri_labels.get(same_as.get(nombre_o_uri, ""), nombre_o_uri))

# Prueba de resolución de términos y URIs
for termino in ["París", "[http://geo.example/city/paris](http://geo.example/city/paris)", "París Hilton"]:
    print(termino, "->", resolver(termino))
```

* **Pregunta de cierre** El riesgo principal es la corrupción o colapso lógico del grafo debido a inferencias erróneas. Si unimos dos entidades distintas mediante un falso positivo de owl:sameAs, el motor de inferencia (reasoner) asumirá que ambas cosas son idénticas en el mundo real y fusionará todas sus propiedades.

Ejemplo concreto: Si enlazamos por error http://geo.example/city/paris (la ciudad) con http://people.example/paris_hilton (la persona) usando owl:sameAs, la máquina deducirá disparates lógicos como que Paris Hilton es la capital de Francia o que la ciudad de París es un recurso de tipo Persona.

## Misión 3 — Mini-grafo en Python y consultas tipo SPARQL

### Código completado y ejecución (Tareas A, B y C)

A continuación se muestra el script de Python con el `patron_b` desarrollado. Para resolver la **Tarea B**, dado que `consulta_simple` evalúa un solo patrón de triple a la vez (no soporta JOINs directos en un solo paso), se realiza una consulta secuencial: primero filtramos los sujetos que son de tipo `ex:Persona` y luego recuperamos sus respectivos nombres.

```python
# Grafo base
G = [
    {"s": "ex:alicia", "p": "tipo", "o": "ex:Persona"},
    {"s": "ex:alicia", "p": "nombre", "o": "Alicia García"},
    {"s": "ex:alicia", "p": "conoce", "o": "ex:bob"},
    {"s": "ex:bob", "p": "nombre", "o": "Bob Martínez"},
    {"s": "ex:bob", "p": "tipo", "o": "ex:Persona"},
    {"s": "ex:libro42", "p": "titulo", "o": "Introducción a la Web Semántica"},
    {"s": "ex:libro42", "p": "autor", "o": "ex:alicia"},
    {"s": "ex:libro42", "p": "autor", "o": "ex:bob"},
    {"s": "ex:libro42", "p": "anio", "o": "2019"},
]

def consulta_simple(g, patron):
    resultados = []
    for t in g:
        asignacion = {}
        ok = True
        for rol in ("s", "p", "o"):
            esperado = patron.get(rol)
            if esperado is None:
                continue
            if t[rol] != esperado:
                ok = False
                break
        if not ok:
            continue
        for rol in ("s", "p", "o"):
            if patron.get(rol) is None:
                asignacion[rol] = t[rol]
        if asignacion and asignacion not in resultados:
            resultados.append(asignacion)
    return resultados

# TAREA A: ¿Quiénes son autores del libro42?
# Nota: El patrón original del enunciado tenía invertido el orden conceptual del triple. 
# Lo correcto de acuerdo a G es: el sujeto es ex:libro42, el predicado es "autor" y el objeto es la variable (?persona).
patron_a = {"s": "ex:libro42", "p": "autor", "o": None}
print("Autores del libro42:", consulta_simple(G, patron_a))


# TAREA B: Pares (persona, nombre) donde persona tiene tipo ex:Persona
print("\n--- Ejecutando Tarea B ---")
# Paso 1: Encontrar las URIs que cumplen con ser tipo ex:Persona
patron_b_tipo = {"s": None, "p": "tipo", "o": "ex:Persona"}
personas = consulta_simple(G, patron_b_tipo)

# Paso 2: Iterar sobre esas personas encontradas para extraer sus nombres correspondientes
for p in personas:
    uri_persona = p["s"]
    patron_b_nombre = {"s": uri_persona, "p": "nombre", "o": None}
    resultado_nombre = consulta_simple(G, patron_b_nombre)
    if resultado_nombre:
        print(f"Persona: {uri_persona} -> Nombre: {resultado_nombre[0]['o']}")


# TAREA C: Añadir un triple inferido manualmente
# Regla informal: si X conoce Y y Y es tipo Persona -> X tieneConocidoPersona Y
# En el grafo, ex:alicia conoce a ex:bob, y ex:bob es ex:Persona.
G.append({"s": "ex:alicia", "p": "tieneConocidoPersona", "o": "ex:bob"})
print("\nTriple inferido manualmente añadido a G.")
```

* **Salida en consola** 
Autores del libro42: [{'o': 'ex:alicia'}, {'o': 'ex:bob'}]

--- Ejecutando Tarea B ---
Persona: ex:alicia -> Nombre: Alicia García
Persona: ex:bob -> Nombre: Bob Martínez

Triple inferido manualmente añadido a G.

* **Análisis: consulta_simple vs Cláusula WHERE de SPARQL**
* En qué se parece: Se asemeja en el concepto fundamental de coincidencia de patrones de grafos (Graph Pattern Matching). Al igual que en SPARQL, se definen elementos fijos (constantes conocidas) y elementos declarados como None, los cuales actúan exactamente como las variables (?variable) de SPARQL buscando mapear elementos compatibles del grafo.

* En qué se queda corta: Se queda corta principalmente en que no maneja la conjunción de múltiples triples (Basic Graph Patterns complejos) en una sola operación. No puede realizar un JOIN automático compartiendo una variable en común (lo que obligó en la Tarea B a hacer un bucle manual en Python). Tampoco tiene soporte para filtros condicionales (FILTER), uniones de patrones (UNION), elementos opcionales (OPTIONAL), ni capacidades de agregación (COUNT, GROUP BY).

* Reflexión: ¿Qué haría un Reasoner OWL real?
En el ejercicio de la Tarea C, tuvimos que inyectar el nuevo conocimiento de forma manual usando lógica imperativa en Python. Un reasoner OWL real opera bajo un enfoque declarativo basado en lógica formal de descripción. En lugar de codificar la inserción a mano, al reasoner se le define una regla ontológica abstracta (por ejemplo, una restricción de propiedad o una regla SWRL). El motor analiza la semántica del grafo de manera autónoma, deduce que ex:alicia cumple las condiciones y genera/asume los triples derivados automáticamente al vuelo durante las consultas sin alterar la base de datos física de forma estática.

**Consulta de la Tarea A en Pseudocódigo SPARQL**
PREFIX ex: [http://ejemplo.org/](http://ejemplo.org/)

SELECT ?persona
WHERE {
    ex:libro42 ex:autor ?persona .
}

## Misión 4 — Primer contacto con RDF en Python

### Código del script utilizando `rdflib`
Para esta misión opcional, importamos la biblioteca estándar de la Web Semántica para Python (`rdflib`), cargamos parte de los triples diseñados en la Misión 1 utilizando URIs reales basadas en el espacio de nombres (Namespace) de ejemplo, y ejecutamos una consulta SPARQL real sobre el grafo en memoria.

```python
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF

# 1. Inicializar el grafo y el espacio de nombres
EX = Namespace("[http://ejemplo.org/](http://ejemplo.org/)")
g = Graph()

# 2. Cargar los triples diseñados en la Misión 1
# Formato de los triples en rdflib: (Sujeto, Predicado, Objeto)
g.add((EX.alicia, EX.tieneNombre, Literal("Alicia García", lang="es")))
g.add((EX.alicia, EX.tieneRol, Literal("Profesora de Matemáticas en la UNAM", lang="es")))
g.add((EX.alicia, EX.conoce, EX.bob))
g.add((EX.bob, EX.tieneNombre, Literal("Bob Martínez", lang="es")))

g.add((EX.libro42, EX.titulo, Literal("Introducción a la Web Semántica", lang="es")))
g.add((EX.libro42, EX.tieneAutor, EX.alicia))
g.add((EX.libro42, EX.tieneAutor, EX.bob))

# 3. Ejecutar una consulta SPARQL mínima para recuperar los nombres cargados
print("--- Resultados de la consulta SPARQL con rdflib ---")
consulta_sparql = """
    SELECT ?nombre 
    WHERE { 
        ?persona [http://ejemplo.org/tieneNombre](http://ejemplo.org/tieneNombre) ?nombre .
    }
"""

for row in g.query(consulta_sparql):
    print(f"Nombre encontrado: {row.nombre}")
```

**Salida en consola**
--- Resultados de la consulta SPARQL con rdflib ---
Nombre encontrado: Alicia García
Nombre encontrado: Bob Martínez

## Puente al tema 5
* ¿Qué problema de esta actividad resuelve RDF que no resuelve solo JSON?
JSON es un formato excelente para el transporte de datos estructurados dentro de sistemas cerrados, pero carece de un marco semántico global: es jerárquico (árbol) y sus claves son simples cadenas de texto locales susceptibles a la colisión de nombres y la ambigüedad. RDF resuelve este problema de raíz al mapear las relaciones como un grafo plano donde cada sujeto, predicado y objeto no literal es obligatoriamente una URI única global.
Esto permite la interoperabilidad semántica universal automática; con RDF se pueden fusionar e interconectar grafos heterogéneos provenientes de distintas fuentes independientes en la web (como el HTML y el JSON de la Misión 1) sin necesidad de reescribir código para mapear traducciones o alias jerárquicos, garantizando que una máquina distinga sin ambigüedades contextos complejos y unifique identidades mediante estándares compartidos.