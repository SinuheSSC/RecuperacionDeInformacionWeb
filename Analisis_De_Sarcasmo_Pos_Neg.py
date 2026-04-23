import re
import nltk
import csv
import pandas as pd
import os
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import wordpunct_tokenize

# ─────────────────────────────────────────────
# 5 algoritmos de aprendizaje supervisado, no superisado y semi-supervisado
# PARTE 0 — 200 comentarios de X (Twitter)
# Mezcla de sarcásticos y no sarcásticos sobre
# tecnología, política, vida cotidiana y cultura.
# ─────────────────────────────────────────────
# Ruta de tu archivo (usamos 'r' al principio para que Python no confunda las diagonales invertidas)
path_csv = r"E:\Mi_Usuario\Documents\RecuperacionWeb\sentiment_analysis_dataset.csv"

# Cargamos el archivo
df = pd.read_csv(path_csv, encoding='utf-8')

# Extraemos la columna 'texto'
comentarios = df['text'].astype(str).tolist()

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
    
    # (Nuevos ejemplos adaptados al CSV)
    ("Qué genial estar colapsado de trabajo un viernes a las 8 p.m. Justo mi plan ideal.", "sar"),
    ("Oh sí, me encanta sentirme abrumado por deudas, es mi deporte favorito.", "sar"),
    ("Qué sorpresa, el sitio está saturado justo cuando salen las entradas. Nadie lo vio venir.", "sar"),
    ("Fantástico, amanecer con el apartamento inundado. La mejor forma de empezar el día.", "sar"),
    ("Me fascina que el hospital esté saturado y me manden a casa con un paracetamol. Gran servicio.", "sar"),
    ("Claro, porque estar incapacitado dos meses es como tener vacaciones pagadas. Qué suerte.", "sar"),
    ("Qué conveniente que el sistema colapse justo cuando tengo que entregar el proyecto.", "sar"),
    ("Obvio que el tráfico está colapsado, si solo cerraron la avenida principal. Qué genios.", "sar"),
    ("Oh, qué sorpresa, me siento confundido por décima vez hoy. Mi cerebro es una joya.", "sar"),
    ("Súper práctico el silencio incómodo en la cena familiar. Muy ameno todo.", "sar"),

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

    # (Nuevos ejemplos adaptados al CSV)
    ("Me siento muy abrumado por la cantidad de cosas que tengo que leer hoy.", "no_sar"),
    ("El sistema de salud está colapsado y la situación es realmente preocupante.", "no_sar"),
    ("Estoy muy preocupado por la salud de mi papá, espero que mejore pronto.", "no_sar"),
    ("Me siento un poco confundido con las nuevas instrucciones del trabajo.", "no_sar"),
    ("Amanecimos con el patio inundado por la lluvia de anoche.", "no_sar"),
    ("Estoy saturado de mensajes en WhatsApp y no puedo responder a todos ahora.", "no_sar"),
    ("Me puse muy sonrojado cuando me felicitaron delante de todo el equipo.", "no_sar"),
    ("Es difícil ser tímido y tratar de hacer amigos nuevos en la universidad.", "no_sar"),
    ("El médico me dio una incapacidad porque sigo sintiéndome mal físicamente.", "no_sar"),
    ("Hubo un silencio incómodo durante la reunión después de ese comentario.", "no_sar")
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

def get_sarcasm_sentiment(text: str) -> str:
    t = normalize_text(text)
    # Detectamos la "falsa positividad"
    pos_terms = sum(1 for w in ["genial", "increible", "maravilla", "perfecto", "amo", "encanta", "bien"] if w in t)
    neg_terms = sum(1 for w in ["odio", "basura", "horror", "malo", "peor", "terrible"] if w in t)
    
    if pos_terms > neg_terms:
        return "Sarcasmo-Negativo (Falsa Aprobación)"
    elif neg_terms > pos_terms:
        return "Sarcasmo-Positivo (Ironía sobre lo malo)"
    else:
        return "Sarcasmo-Neutral/Irónico"

CONFIDENCE_THRESHOLD = 0.55
out_rows = []

for text in comentarios:
    feats = featurize(text)
    dist  = classifier.prob_classify(feats)
    nb_label = dist.max()
    nb_prob  = float(dist.prob(nb_label))

    # 1. Decisión de etiqueta (Naive Bayes vs Léxico)
    if nb_prob < CONFIDENCE_THRESHOLD:
        final_label = lexicon_sarcasm(text)
        method = "lexicon_fallback"
    else:
        final_label = nb_label
        method = "naive_bayes"

    # 2. Análisis de sentimiento de segundo nivel (solo si es sarcasmo)
    sub_sentiment = "N/A"
    if final_label == "sar":
        sub_sentiment = get_sarcasm_sentiment(text)

    # 3. Guardar todo en una sola fila
    out_rows.append((text, final_label, round(nb_prob, 4), method, sub_sentiment))

print(f"✅ Procesamiento completado. Analizados {len(out_rows)} comentarios.")



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
# PASO 7 — Reporte de resultados corregido
# ─────────────────────────────────────────────
sarcasticos    = [r for r in out_rows if r[1] == "sar"]
no_sarcasticos = [r for r in out_rows if r[1] == "no_sar"]
nb_count       = sum(1 for r in out_rows if r[3] == "naive_bayes")
lex_count      = sum(1 for r in out_rows if r[3] == "lexicon_fallback")

print("=" * 60)
print("RESUMEN DE DETECCIÓN DE SARCASMO")
print("=" * 60)
print(f"Total de comentarios analizados : {len(out_rows)}")
print(f"Detectados como sarcásticos     : {len(sarcasticos)}")
print(f"Detectados como no sarcásticos  : {len(no_sarcasticos)}")
print(f"Clasificados por Naive Bayes    : {nb_count}")
print(f"Clasificados por léxico         : {lex_count}")
print()

print("─── MUESTRA: Sarcásticos detectados (Texto | Prob | Sentimiento Real) ───")
# Añadimos 'sent' para desempacar el 5to valor
for t, lab, prob, method, sent in sarcasticos[:8]:
    print(f"  [{prob:.2f}] {t[:60]}... -> {sent}")

print()
print("─── MUESTRA: No sarcásticos (primeros 5) ───")
# También corregimos aquí para evitar el error si decides imprimir no_sarcásticos
for t, lab, prob, method, sent in no_sarcasticos[:5]:
    print(f"  [{prob:.2f}] {t[:75]}...")

print()
print("─── ANÁLISIS DE INTENCIÓN EN SARCASMO ───")
sar_neg = sum(1 for r in sarcasticos if "Sarcasmo-Negativo" in r[4])
sar_pos = sum(1 for r in sarcasticos if "Sarcasmo-Positivo" in r[4])
print(f"Sarcasmos con intención Negativa (Quejas): {sar_neg}")
print(f"Sarcasmos con intención Positiva (Elogios): {sar_pos}")

print()
print("─── Features más informativas del modelo ───")
classifier.show_most_informative_features(12)