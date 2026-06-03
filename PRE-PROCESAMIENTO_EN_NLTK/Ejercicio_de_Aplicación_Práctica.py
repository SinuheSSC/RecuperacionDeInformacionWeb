import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist

# Aseguramos la descarga de los recursos necesarios (incluyendo punkt_tab por la versión actual)
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

# 1. Selección del abstract (Área: Inteligencia Artificial / Deep Learning)
abstract = """
La inteligencia artificial ha transformado radicalmente la investigación científica contemporánea. 
Las redes neuronales artificiales, inspiradas en la estructura biológica del cerebro humano, 
permiten procesar volúmenes masivos de datos para identificar patrones complejos que antes 
eran invisibles para los métodos estadísticos tradicionales. En este contexto, el aprendizaje 
profundo o deep learning se ha consolidado como la arquitectura predominante para tareas de 
visión computacional y procesamiento de lenguaje natural. Sin embargo, a pesar de su gran 
capacidad de predicción, estos modelos a menudo funcionan como cajas negras, lo que plantea 
desafíos significativos en términos de interpretabilidad y ética. El desarrollo de una 
inteligencia artificial más transparente y explicable es fundamental para su integración 
segura en áreas críticas como la medicina, las finanzas y la seguridad nacional, donde 
comprender el razonamiento detrás de una decisión es tan importante como la precisión del sistema.
"""

# --- PIPELINE DE PRE-PROCESAMIENTO ---

# A. Tokenización original
tokens_originales = word_tokenize(abstract, language='spanish')

# B. Normalización (minúsculas), limpieza (solo alfabético) y eliminación de Stopwords
vocabulario_stopwords = set(stopwords.words('spanish'))

tokens_procesados = [
    token.lower() for token in tokens_originales 
    if token.isalpha() and token.lower() not in vocabulario_stopwords
]

# --- CÁLCULOS SOLICITADOS ---

# 1. Conteo de tokens
total_originales = len(tokens_originales)
total_procesados = len(tokens_procesados)

# 2. Porcentaje de reducción (Fórmula: (Original - Procesado) / Original * 100)
reduccion = ((total_originales - total_procesados) / total_originales) * 100

# 3. Distribución de frecuencias
distribucion = FreqDist(tokens_procesados)

# --- SALIDA DE RESULTADOS (stdout) ---

print("="*50)
print("RESULTADOS DEL PRE-PROCESAMIENTO NLP")
print("="*50)
print(f"• Número total de tokens originales: {total_originales}")
print(f"• Número total de tokens tras pre-procesamiento: {total_procesados}")
print(f"• Porcentaje de reducción de dimensionalidad: {reduccion:.2f}%")
print("-"*50)
print("• Los 5 términos más frecuentes:")
for termino, frecuencia in distribucion.most_common(5):
    print(f"  - {termino}: {frecuencia} apariciones")
print("="*50)