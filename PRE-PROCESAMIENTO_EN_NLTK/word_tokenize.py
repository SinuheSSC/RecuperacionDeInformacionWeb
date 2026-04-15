from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist

  
texto_crudo = "El procesamiento de señales y el análisis de texto comparten principios matemáticos fundamentales." 
# Generación de la lista de tokens
tokens = word_tokenize(texto_crudo, language='spanish')
   
print("Longitud de la cadena original:", len(texto_crudo), "caracteres")
print("Cantidad de tokens generados:", len(tokens))
print("Vector de tokens:", tokens)

# 1. Plegado de mayúsculas (Case folding)
tokens_normalizados = [token.lower() for token in tokens]
# 2. Filtrado de caracteres especiales y signos de puntuación
# La función .isalpha() evalúa si el string contiene únicamente caracteres alfabéticos
tokens_limpios = [token for token in tokens_normalizados if token.isalpha()]
 
print("Tokens tras normalización y filtrado:", tokens_limpios)

# Carga del conjunto (set) de palabras vacías para el idioma español
vocabulario_stopwords = set(stopwords.words('spanish'))
# Filtrado mediante exclusión
tokens_con_significado = [token for token in tokens_limpios if token not in vocabulario_stopwords]
print("Vector de características final:", tokens_con_significado)

documento = """
  La arquitectura de computadoras define la estructura y el comportamiento de un sistema informático. 
  Una buena arquitectura optimiza el rendimiento del sistema y minimiza el consumo de energía. 
  El diseño de la estructura del sistema es un desafío constante en la ingeniería de computadoras.
  """
 
# Pipeline integrado
tokens_doc = word_tokenize(documento, language='spanish')
tokens_procesados = [t.lower() for t in tokens_doc if t.isalpha() and t.lower() not in vocabulario_stopwords] 
# Cálculo de la distribución de frecuencias
distribucion = FreqDist(tokens_procesados)
 
print("Términos con mayor frecuencia absoluta (Top 3):")
for termino, frecuencia in distribucion.most_common(3):
    print(f"- {termino}: {frecuencia} apariciones")

