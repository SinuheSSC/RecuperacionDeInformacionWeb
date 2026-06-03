import feedparser
import json
import re

def clean_text(text):
    """Elimina etiquetas HTML y normaliza el texto."""
    if not text:
        return ""
    # 1. Quitar etiquetas HTML
    text = re.sub(r"<[^>]+>", " ", text)
    # 2. Quitar caracteres especiales (deja letras, números y espacios)
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    # 3. Colapsar espacios en blanco y pasar a minúsculas
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text

def fetch_rss(url, max_entries=20):
    """Devuelve una lista de ítems de un feed RSS/Atom procesados."""
    feed = feedparser.parse(url)
    items = []
    
    for e in feed.entries[:max_entries]:
        title = e.get("title", "")
        summary = e.get("summary", e.get("description", ""))
        
        # Procesamos la limpieza aquí mismo
        items.append({
            "title": title,
            "link": e.get("link", ""),
            "published": e.get("published", e.get("updated", "")),
            "summary": summary,
            "text_clean": f"{clean_text(title)} {clean_text(summary)}"
        })
    return items

# --- Configuración y ejecución ---

urls = [
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/mexico/portada",
    "https://www.reddit.com/r/python/.rss",
    "https://hnrss.org/frontpage",
    "https://www.gamereactor.es/rss/rss.php?texttype=[4,1,2,3,5,9,10,7,8,11]"
]

feeds_data = {}

for url in urls:
    try:
        print(f"Procesando: {url}")
        feeds_data[url] = fetch_rss(url, max_entries=10)
    except Exception as err:
        feeds_data[url] = [{"error": str(err)}]

# Guardar datos en un archivo JSON (con el campo limpio incluido)
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(feeds_data, f, indent=2, ensure_ascii=False)

print("\n¡Hecho! Datos guardados en data.json sin etiquetas HTML en el campo 'text_clean'.")