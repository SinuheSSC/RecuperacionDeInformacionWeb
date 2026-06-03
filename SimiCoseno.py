from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

STOP_WORDS_ES = [
    "a", "acá", "ahí", "al", "algo", "algún", "alguna", "algunas", "alguno",
    "algunos", "allá", "allí", "ante", "antes", "aquel", "aquella", "aquellas",
    "aquello", "aquellos", "aquí", "así", "aún", "bajo", "bastante", "bien",
    "cabe", "cada", "casi", "como", "con", "contra", "cual", "cuales",
    "cualquier", "cualquiera", "cualquieras", "cuán", "cuándo", "cuánto",
    "de", "dejar", "del", "demás", "demasiado", "donde", "dos", "el", "él",
    "ella", "ellas", "ellos", "en", "entre", "era", "eran", "eres", "es",
    "esa", "esas", "ese", "eso", "esos", "esta", "está", "están", "estas",
    "este", "esto", "estos", "estoy", "fue", "fueron", "fui", "ha", "han",
    "hasta", "hay", "la", "las", "le", "les", "lo", "los", "más", "me",
    "mi", "mis", "mucha", "muchas", "mucho", "muchos", "muy", "nada",
    "ni", "no", "nos", "nosotros", "nuestra", "nuestras", "nuestro",
    "nuestros", "o", "os", "otra", "otras", "otro", "otros", "para",
    "pero", "poco", "por", "porque", "que", "qué", "quien", "quién",
    "quienes", "se", "sea", "según", "ser", "si", "sí", "sin", "sobre",
    "so", "somos", "son", "su", "sus", "también", "tan", "tanto", "te",
    "tenemos", "tener", "tiene", "tienen", "toda", "todas", "todavía",
    "todo", "todos", "tu", "tus", "un", "una", "uno", "unos", "usted",
    "ustedes", "ya", "yo"
]

def cargar_documentos(directorio: str):
    base_path = Path(directorio)
    filepaths = sorted(base_path.glob("*.txt"))

    documentos = []
    nombres = []

    for path in filepaths:
        texto = path.read_text(encoding="utf-8", errors="ignore")
        documentos.append(texto)
        nombres.append(path.name)

    return nombres, documentos


def calcular_tfidf(documentos):
    vectorizador = TfidfVectorizer(
        lowercase=True,
        stop_words=STOP_WORDS_ES  # aquí pasamos la lista
    )
    matriz_tfidf = vectorizador.fit_transform(documentos)
    return matriz_tfidf, vectorizador


def matriz_similitud_coseno(matriz_tfidf):
    return cosine_similarity(matriz_tfidf)


if __name__ == "__main__":
    nombres, documentos = cargar_documentos("SimiCosenoTextos")
    matriz_tfidf, vectorizador = calcular_tfidf(documentos)
    sim_matrix = matriz_similitud_coseno(matriz_tfidf)

    print("Documentos cargados:")
    for i, nombre in enumerate(nombres):
        print(f"{i}: {nombre}")

    print("\nMatriz de similitud de coseno:")
    print(sim_matrix)

    if len(nombres) >= 2:
        print(
            f"\nSimilitud de coseno entre '{nombres[0]}' y '{nombres[1]}': "
            f"{sim_matrix[0, 1]:.4f}"
        )