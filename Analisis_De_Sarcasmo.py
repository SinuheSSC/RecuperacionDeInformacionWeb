import re
import nltk
import csv
import pandas as pd
import os
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import wordpunct_tokenize

# ─────────────────────────────────────────────
# PARTE 0 — 200 comentarios de X (Twitter)
# Mezcla de sarcásticos y no sarcásticos sobre
# tecnología, política, vida cotidiana y cultura.
# ─────────────────────────────────────────────
# Ruta de tu archivo (usamos 'r' al principio para que Python no confunda las diagonales invertidas)
path_csv = r"E:\Mi_Usuario\Documents\RecuperacionWeb\sentimientos_socialtox_200.csv"

# Cargamos el archivo
df = pd.read_csv(path_csv, encoding='utf-8')

# Extraemos la columna 'texto'
comentarios = df['texto'].astype(str).tolist()

print(f"✅ Se cargaron {len(comentarios)} comentarios reales de X.")

# ─────────────────────────────────────────────
# PASO 1 — Recursos NLTK
# ─────────────────────────────────────────────
def ensure_nltk_resources():
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
    ]
    for path, name in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=False)

ensure_nltk_resources()
print("NLTK OK.")

# ─────────────────────────────────────────────
# PASO 2 — Normalización
# ─────────────────────────────────────────────
_URL_RE        = re.compile(r"https?://\S+|www\.\S+")
_MENTION_RE    = re.compile(r"@\w+")
_HASHTAG_RE    = re.compile(r"#\w+")
_NON_LETTER_RE = re.compile(r"[^a-záéíóúñü0-9\s!?\"\'¡¿]+", re.IGNORECASE)
_MULTISPACE_RE = re.compile(r"\s+")

def normalize_text(text: str) -> str:
    t = text.strip().lower()
    t = _URL_RE.sub(" ", t)
    t = _MENTION_RE.sub(" ", t)
    t = _HASHTAG_RE.sub(" ", t)
    t = _NON_LETTER_RE.sub(" ", t)
    t = _MULTISPACE_RE.sub(" ", t).strip()
    return t

sw = set(stopwords.words("spanish"))
stemmer = SnowballStemmer("spanish")

# ─────────────────────────────────────────────
# PASO 3 — Extracción de características
#
# Señales clave de sarcasmo en español:
#   1. Palabras positivas + contexto negativo ("genial", "claro", "obvio", "seguro", "qué sorpresa")
#   2. Construcciones retóricas de sarcasmo
#   3. Puntuación exagerada (!!, ??)
#   4. Comillas de distanciamiento
#   5. Frases de falsa sorpresa o fingida aprobación
# ─────────────────────────────────────────────

# Marcadores lingüísticos de sarcasmo en español
SARCASM_TRIGGERS = {
    "claro que", "obvio que", "seguro que", "con razón", "qué sorpresa",
    "qué conveniente", "qué útil", "qué genial", "qué maravilla",
    "genial", "fantástico", "increíble", "perfecto", "súper práctico",
    "qué emocionante", "impresionante", "justo lo que",
    "nunca pasa", "nunca falla", "siempre pasa", "como siempre",
    "definitivamente", "por supuesto", "naturalmente",
    "muy profundo", "muy lógico", "muy inteligente", "muy innovador",
    "en el universo paralelo", "primer mundo",
}

# Intensificadores negativos reales (sin sarcasmo aparente)
GENUINE_NEG = {
    "error", "falla", "problema", "bug", "lento", "tardó", "frustrant",
    "roto", "no funciona", "se cayó", "expiró", "perdimos",
}

GENUINE_POS = {
    "mejoró", "funciona", "resolvieron", "eficiente", "correcto",
    "precisión", "exitoso", "completó", "sin errores", "buen trabajo",
}

def featurize(text: str) -> dict:
    t_norm = normalize_text(text)
    tokens = wordpunct_tokenize(t_norm)
    feats = {}

    # Stems de palabras con stopwords removidas
    stems = []
    for tok in tokens:
        if tok.isdigit():
            feats["HAS_NUMBER"] = True
            continue
        if len(tok) < 2:
            continue
        if tok in sw:
            continue
        stem = stemmer.stem(tok)
        stems.append(stem)
        feats[f"w={stem}"] = True

    # ── Señales de sarcasmo ──────────────────────────────

    # 1. Marcadores explícitos de sarcasmo
    sarcasm_hits = sum(1 for trigger in SARCASM_TRIGGERS if trigger in t_norm)
    feats["SARCASM_TRIGGER_COUNT"] = sarcasm_hits > 0
    feats["SARCASM_TRIGGER_MULTIPLE"] = sarcasm_hits >= 2

    # 2. Puntuación exagerada
    feats["DOUBLE_EXCLAMATION"] = "!!" in text or text.count("!") >= 2
    feats["DOUBLE_QUESTION"]    = "??" in text or text.count("?") >= 2
    feats["EXCLAMATION"]        = "!" in text
    feats["MIXED_PUNCT"]        = "!?" in text or "?!" in text

    # 3. Comillas (distanciamiento irónico)
    feats["HAS_QUOTES"] = ('"' in text or "'" in text or
                           "\u201c" in text or "\u201d" in text or
                           "\u2018" in text or "\u2019" in text)

    # 4. Contraste: palabra positiva + contexto negativo en la misma oración
    has_pos_word = any(w in t_norm for w in ["genial", "perfecto", "increíble",
                                              "fantástico", "maravilla", "excelente",
                                              "claro", "obvio", "seguro"])
    has_neg_context = any(w in t_norm for w in GENUINE_NEG)
    feats["POSITIVE_NEG_CONTRAST"] = has_pos_word and has_neg_context

    # 5. Frases de fingida sorpresa / falsa aprobación al inicio
    feats["STARTS_WITH_SARCASM"] = any(
        t_norm.startswith(p) for p in [
            "claro", "obvio", "genial", "fantástic", "increíble",
            "sí segur", "oh sí", "oh", "qué sorpresa", "qué conveniente",
            "seguramente", "con razón", "qué útil", "qué bien",
        ]
    )

    # 6. Negación real (distinguir del sarcasmo sin negación)
    feats["HAS_NEGATION"] = any(w in t_norm.split() for w in
                                ("no", "nunca", "jamás", "ni", "tampoco", "sin"))

    # 7. Longitud del tweet
    feats["LEN_GT_100"] = len(t_norm) > 100
    feats["LEN_LT_50"]  = len(t_norm) < 50

    # 8. Mayúsculas en texto original (énfasis irónico)
    upper_words = sum(1 for w in text.split() if w.isupper() and len(w) > 2)
    feats["HAS_ALL_CAPS"] = upper_words > 0

    # 9. Palabras positivas genuinas (indicador de no sarcasmo)
    feats["GENUINE_POSITIVE"] = any(w in t_norm for w in GENUINE_POS)

    return feats

print("Features de muestra:", list(featurize(comentarios[0]).keys())[:10])

# ─────────────────────────────────────────────
# PASO 4 — Datos de entrenamiento etiquetados
#
# Etiquetas: "sar" (sarcástico) | "no_sar" (literal)
# ─────────────────────────────────────────────
train_data = [
    # ─── SARCÁSTICOS (Etiqueta: sar) ───
    # (Tus ejemplos tecnológicos originales)
    ("Claro, seguro que el nuevo iPhone vale 1500 dólares porque es de oro.", "sar"),
    ("Qué sorpresa tan inesperada, el tren llegó tarde otra vez.", "sar"),
    ("Oh sí, definitivamente necesitaba cinco actualizaciones en un solo día.", "sar"),
    ("Claro que el jefe tiene razón, siempre la tiene.", "sar"),
    ("Fantástico, otra reunión que perfectamente podría haber sido un correo.", "sar"),
    ("Increíble cómo mejoró la app después de la actualización, no abre pero mejoró.", "sar"),
    ("Con razón cobran 20 pesos por la bolsa, el servicio es de primer mundo.", "sar"),
    ("Sí, el candidato tiene toda la razón, todo era mejor antes. Muy profundo.", "sar"),
    ("Obvio que el algoritmo me recomienda lo que ya compré. Super inteligente.", "sar"),
    ("Qué conveniente que la app pida actualizar justo cuando vas a usarla.", "sar"),
    
    # (Nuevos ejemplos adaptados a tu CSV: Política y Sociedad)
    ("Qué justicia más injusta tenemos, qué maravilla de sistema.", "sar"),
    ("Claro, porque dejar la economía en esas manos solo trae prosperidad.", "sar"),
    ("Qué sorpresa, el político prometió lo mismo de hace cuatro años. Qué innovador.", "sar"),
    ("Genial, otra ley que arregla todo mágicamente sin cambiar nada.", "sar"),
    ("Obvio que los impuestos son para nuestro bien, se nota en las carreteras.", "sar"),
    ("Qué útil es el manual de seguridad cuando ya pasó la emergencia. Muy previsores.", "sar"),
    ("Seguro que la culpa es de los rusos o de Franco, como siempre.", "sar"),
    ("Qué democrático silenciar al que piensa distinto. Todo un ejemplo de libertad.", "sar"),
    ("Claro que el sistema electoral es perfecto y sin fallos. Qué transparencia.", "sar"),
    ("¡Uy sí, qué gran cambio! Han puesto a los mismos de siempre en puestos nuevos.", "sar"),

    # ─── NO SARCÁSTICOS / LITERALES (Etiqueta: no_sar) ───
    # (Tus ejemplos tecnológicos originales)
    ("Acabo de actualizar el sistema y todo funciona perfectamente.", "no_sar"),
    ("El nuevo modelo de lenguaje tiene mejoras reales en razonamiento.", "no_sar"),
    ("El soporte técnico resolvió mi problema en menos de diez minutos.", "no_sar"),
    ("Por fin entendí cómo funciona la recursividad, el tutorial estaba muy bien.", "no_sar"),
    ("La reunión fue corta y productiva, definimos el roadmap completo.", "no_sar"),
    ("El rediseño de la app es mucho más intuitivo que la versión anterior.", "no_sar"),
    ("Pude migrar la base de datos sin perder ningún registro.", "no_sar"),
    ("El modelo de clasificación alcanzó un 94% de accuracy.", "no_sar"),
    ("El parche de seguridad se instaló sin afectar ninguna funcionalidad.", "no_sar"),
    ("La función de autocompletado del IDE sugiere correctamente los nombres.", "no_sar"),

    # (Nuevos ejemplos adaptados a tu CSV: Literalidad política/social)
    ("Es necesario cambiar las leyes y las penas porque esto irá a peor.", "no_sar"),
    ("La victoria fue gracias a la alianza entre soviéticos y estadounidenses.", "no_sar"),
    ("El sistema de monitoreo envió la alerta antes de que fallara el disco.", "no_sar"),
    ("Fuerza Dani, eres un gran héroe para todos los animales.", "no_sar"),
    ("La Constitución garantiza el derecho a la autonomía de las regiones.", "no_sar"),
    ("El presupuesto para defensa aumentará gradualmente en el año 2023.", "no_sar"),
    ("La fiscalía ha solicitado los documentos para iniciar la investigación.", "no_sar"),
    ("Muchos ciudadanos están cansados de la corrupción en las instituciones.", "no_sar"),
    ("El debate fue intenso pero se mantuvieron las formas democráticas.", "no_sar"),
    ("Se requiere un análisis serio de los datos económicos antes de decidir.", "no_sar"),
]

train_set = [(featurize(text), label) for text, label in train_data]
classifier = nltk.NaiveBayesClassifier.train(train_set)
print(f"Entrenamiento OK. {len(train_set)} ejemplos.")

# ─────────────────────────────────────────────
# PASO 5 — Predicción + regla léxica de respaldo
#
# Si el clasificador NB no tiene confianza alta
# (prob < 0.65), se aplica la regla léxica como
# desempate para reducir falsos negativos.
# ─────────────────────────────────────────────
def lexicon_sarcasm(text: str) -> str:
    t = normalize_text(text)
    hits = sum(1 for trigger in SARCASM_TRIGGERS if trigger in t)
    starts_ironically = any(
        t.startswith(p) for p in [
            "claro", "obvio", "genial", "fantástic",
            "sí segur", "oh sí", "qué sorpresa", "con razón",
        ]
    )
    if hits >= 2 or (hits == 1 and starts_ironically):
        return "sar"
    return "no_sar"

CONFIDENCE_THRESHOLD = 0.55
out_rows = []

for text in comentarios:
    feats = featurize(text)
    dist  = classifier.prob_classify(feats)
    nb_label = dist.max()
    nb_prob  = float(dist.prob(nb_label))

    if nb_prob < CONFIDENCE_THRESHOLD:
        # Usar léxico como desempate
        final_label = lexicon_sarcasm(text)
        method = "lexicon_fallback"
        final_prob = nb_prob
    else:
        final_label = nb_label
        method = "naive_bayes"
        final_prob = nb_prob

    out_rows.append((text, final_label, round(final_prob, 4), method))

# ─────────────────────────────────────────────
# PASO 6 — Exportar resultados
# ─────────────────────────────────────────────
out_path = "sarcasmo_resultados.csv"
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["texto", "etiqueta", "probabilidad", "metodo"])
    for row in out_rows:
        w.writerow(row)

print(f"Archivo generado: {out_path}\n")

# ─────────────────────────────────────────────
# PASO 7 — Reporte de resultados
# ─────────────────────────────────────────────
sarcasticos   = [r for r in out_rows if r[1] == "sar"]
no_sarcasticos = [r for r in out_rows if r[1] == "no_sar"]
nb_count      = sum(1 for r in out_rows if r[3] == "naive_bayes")
lex_count     = sum(1 for r in out_rows if r[3] == "lexicon_fallback")

print("=" * 60)
print("RESUMEN DE DETECCIÓN DE SARCASMO")
print("=" * 60)
print(f"Total de comentarios analizados : {len(out_rows)}")
print(f"Detectados como sarcásticos     : {len(sarcasticos)}")
print(f"Detectados como no sarcásticos  : {len(no_sarcasticos)}")
print(f"Clasificados por Naive Bayes    : {nb_count}")
print(f"Clasificados por léxico         : {lex_count}")
print()

print("─── MUESTRA: Sarcásticos detectados (primeros 8) ───")
for t, lab, prob, method in sarcasticos[:8]:
    print(f"  [{prob:.2f}] {t[:75]}...")

print()
print("─── MUESTRA: No sarcásticos (primeros 5) ───")
for t, lab, prob, method in no_sarcasticos[:5]:
    print(f"  [{prob:.2f}] {t[:75]}...")

print()
print("─── Features más informativas del modelo ───")
classifier.show_most_informative_features(12)