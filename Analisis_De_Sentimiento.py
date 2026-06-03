import re
import nltk
import csv
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import wordpunct_tokenize

#PARTE 0
comentarios = [
    "El autocompletado de este IDE es bastante lento cuando el proyecto supera los mil archivos.",
    "La nueva actualización de la extensión de Python arruinó la indentación automática.",
    "Es increíble lo fácil que es configurar un entorno virtual con esta herramienta.",
    "El compilador tardó 45 segundos en generar el binario final.",
    "No entiendo por qué quitaron el botón de acceso rápido al depurador en esta versión.",
    "Me encanta que ahora se integre nativamente con Git sin necesidad de plugins extra.",
    "El modo oscuro de la interfaz tiene un contraste excelente para trabajar de noche.",
    "Siempre que intento abrir un archivo CSV muy grande, el editor se queda congelado.",
    "La refactorización de código se hace casi de manera mágica, me ahorra horas.",
    "El log de errores muestra un mensaje hexadecimal que no ayuda en nada a resolver el problema.",
    "Para esta práctica utilizaremos el framework de React en el frontend.",
    "La documentación oficial está desactualizada respecto a la última versión estable.",
    "Pude resolver el bug de concurrencia gracias a la herramienta de profiling.",
    "El atajo de teclado para comentar bloques de código dejó de funcionar tras actualizar.",
    "El consumo de RAM del entorno de desarrollo no baja de los 4GB, es excesivo.",
    "La sintaxis del lenguaje es muy limpia, pero la curva de aprendizaje del framework es empinada.",
    "Logré implementar el algoritmo de búsqueda en grafos sin utilizar recursividad.",
    "El soporte técnico del IDE tardó tres semanas en responder mi ticket.",
    "Configurar el linter por primera vez es tedioso, aunque después vale la pena.",
    "Se requiere una versión de Node igual o superior a la 18.x para ejecutar el script.",
    "El descriptor SIFT detectó los puntos clave perfectamente incluso con cambios de iluminación.",
    "El modelo de Deep Learning requiere demasiada capacidad de cómputo para lo que hace.",
    "Entrenar esta red neuronal tomó 14 horas continuas en la GPU.",
    "Prefiero usar técnicas clásicas de visión por computadora porque son más predecibles matemáticamente.",
    "La librería de OpenCV falló al intentar abrir el flujo de video de la cámara web.",
    "El dataset original contiene 5,000 imágenes etiquetadas manualmente.",
    "Increíble la precisión que logramos en la detección de bordes usando el filtro de Canny.",
    "El ruido gaussiano en las imágenes médicas está afectando la etapa de segmentación.",
    "El script de preprocesamiento normaliza los píxeles a valores entre 0 y 1.",
    "Los resultados del artículo no son reproducibles porque no publicaron los hiperparámetros.",
    "La API de reconocimiento facial es rapidísima, aunque falla con personas usando mascarilla.",
    "Extraer las características usando SURF fue mucho más eficiente que intentar una red convolucional.",
    "El accuracy del modelo se estancó en 82% sin importar cuántas épocas más lo entrene.",
    "Me fascina la elegancia matemática detrás de las transformadas de Hough.",
    "La función de binarización de Otsu calculó el umbral incorrecto para este lote de fotos.",
    "Reducir la dimensionalidad con PCA mejoró notablemente el tiempo de inferencia.",
    "El clasificador SVM separó las clases con un margen muy claro.",
    "La matriz de confusión muestra demasiados falsos positivos en la clase minoritaria.",
    "El tutorial sobre detección de blobs está muy bien explicado paso a paso.",
    "Al exportar el modelo a ONNX, el tamaño del archivo se redujo a la mitad.",
    "La base de datos relacional completó la migración sin pérdida de registros.",
    "El query de SQL está haciendo un escaneo completo de la tabla y colapsando el servidor.",
    "Excelente latencia en los servidores de la región este, apenas 12ms.",
    "Intentar configurar los contenedores de Docker en Windows sigue siendo un dolor de cabeza.",
    "El balanceador de carga distribuyó el tráfico equitativamente durante el pico de usuarios.",
    "La API REST responde con un error 500 intermitente que nadie sabe explicar.",
    "Me gusta la interfaz de administración del clúster, pero le faltan opciones de monitoreo en tiempo real.",
    "El backup automático se ejecuta todos los días a las 3:00 AM.",
    "Perdimos dos horas de producción porque el certificado SSL expiró y no hubo alerta.",
    "La arquitectura de microservicios hizo que el despliegue fuera extremadamente ágil.",
    "No puedo creer que sigan guardando las contraseñas en texto plano en la base de datos.",
    "El servicio de mensajería asíncrona procesó un millón de eventos por minuto sin problemas.",
    "La conexión al servidor SSH se cierra por timeout cada cinco minutos, es frustrante.",
    "El caché de Redis redujo el tiempo de carga de la página de inicio en un 80%.",
    "El script de automatización borró accidentalmente el directorio de configuraciones.",
    "Desplegar la aplicación en la nube fue mucho más caro de lo que habíamos presupuestado.",
    "La migración a GraphQL simplificó muchísimo las consultas desde las aplicaciones móviles.",
    "El uso de CPU del servidor de base de datos se mantiene estable en 45%.",
    "Restaurar el sistema desde el último snapshot fue rápido e intuitivo.",
    "Las políticas de CORS en este servidor están configuradas de manera demasiado restrictiva.",
    "La rúbrica del proyecto final no especifica si debemos incluir pruebas unitarias.",
    "El profesor explicó maravillosamente el concepto de complejidad algorítmica.",
    "La impresora 3D se atascó a mitad de la noche y arruinó una pieza de 10 horas.",
    "El laminador Cura generó unos soportes imposibles de remover sin romper el modelo.",
    "Las instrucciones de la práctica de laboratorio están llenas de ambigüedades.",
    "Me sorprende la calidad del acabado superficial al imprimir con PETG a esta temperatura.",
    "Reparar el archivo STL con MeshLab fue súper sencillo y rápido.",
    "El examen parcial abarcará desde el capítulo 1 hasta el 4 del libro de texto.",
    "El sistema de gestión escolar se cae siempre en temporada de inscripciones.",
    "Me encantó cómo el asesor de tesis estructuró el cronograma de investigación.",
    "La presentación sobre descriptores visuales me ayudó a entender por qué no todo es Deep Learning.",
    "El aula virtual no permite adjuntar archivos mayores a 5MB, lo cual es inútil para código compilado.",
    "La cama caliente de la impresora no alcanza los 80 grados necesarios para ABS.",
    "El código que compartieron en el repositorio de la clase compila a la primera.",
    "Las calificaciones del primer corte ya fueron publicadas en el portal institucional.",
    "Aunque la teoría fue densa, los ejercicios prácticos aterrizaron muy bien los conceptos.",
    "El filamento se rompió por exceso de humedad dentro del extrusor.",
    "Exportar el documento de Org-mode a PDF con LaTeX dio un formato impecable.",
    "La retroalimentación del código fue dura pero extremadamente constructiva.",
    "No tuvimos suficiente tiempo en el laboratorio para terminar de armar el circuito.",
    "La aplicación móvil se cierra sola al intentar usar la cámara en Android 13.",
    "El nuevo diseño del dashboard es moderno y muy intuitivo para el usuario final.",
    "La resolución del monitor secundario no se ajusta correctamente en Linux.",
    "Escribir la documentación técnica en Markdown me resulta muy productivo.",
    "El parche de seguridad solucionó la vulnerabilidad, pero rompió la compatibilidad hacia atrás.",
    "El paquete de instalación incluye un script de desinstalación limpia.",
    "Es la tercera vez esta semana que la VPN corporativa me desconecta sin motivo.",
    "El gestor de dependencias resolvió todos los conflictos de versiones automáticamente.",
    "La animación de carga es fluida y hace que la espera se sienta mucho menor.",
    "Los atajos de teclado me permiten editar texto sin quitar las manos de la posición base.",
    "El sistema reporta una fuga de memoria cada vez que se instancia esa clase.",
    "La actualización del firmware del router tomó menos de cinco minutos.",
    "Trabajar con expresiones regulares largas a menudo resulta en código difícil de mantener.",
    "El modo de depuración paso a paso es la mejor característica de este software.",
    "La batería del teclado inalámbrico dura casi seis meses con uso diario.",
    "Los colores de la terminal por defecto son difíciles de leer contra un fondo oscuro.",
    "Implementar el patrón Singleton aquí resolvió el problema de instancias múltiples.",
    "El foro de la comunidad resolvió mi duda técnica mucho más rápido que el manual oficial.",
    "El framework de pruebas genera reportes de cobertura en formato HTML detallado.",
    "El diseño responsivo de la web falla completamente al visualizarse en tablets en modo horizontal."
]
print("Cantidad de textos:", len(comentarios))

#Paso 1: Descarga de recursos NLTK
def ensure_nltk_resources():
    for resource in ("punkt", "stopwords"):
        try:
            nltk.data.find(f"tokenizers/{resource}" if resource == "punkt" else f"corpora/{resource}")
        except LookupError:
            nltk.download(resource, quiet=False)

ensure_nltk_resources()
print("NLTK OK.")

#Paso 2: Preprocesamiento (normalización, tokenización, stopwords, stemming)
_URL_RE = re.compile(r"https?://\\S+|www\\.\\S+")
_MENTION_RE = re.compile(r"@\\w+")
_HASHTAG_RE = re.compile(r"#\\w+")
_NON_LETTER_RE = re.compile(r"[^a-záéíóúñü0-9\\s]+", re.IGNORECASE)
_MULTISPACE_RE = re.compile(r"\\s+")

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

def featurize(text: str) -> dict:
    t = normalize_text(text)
    tokens = wordpunct_tokenize(t)
    feats = {}
    for tok in tokens:
        if tok.isdigit():
            feats["HAS_NUMBER"] = True
            continue
        if len(tok) < 2:
            continue
        if tok in sw:
            continue
        stem = stemmer.stem(tok)
        feats[f"w={stem}"] = True
    feats["LEN_GT_120"] = len(t) > 120
    feats["HAS_EXCLAMATION"] = "!" in text
    feats["HAS_NEGATION"] = any(w in t.split() for w in ("no", "nunca", "jamás", "ni"))
    return feats

print("Ejemplo normalizado:")
print(normalize_text(comentarios[0]))
print("Features (muestra):", list(featurize(comentarios[0]).keys())[:12])

#Paso 3 (baseline): Sentimiento por léxico simple (reglas)
POS_WORDS = {
    "increíble","fácil","me encanta","excelente","mágica","ahorra","precisión","maravillosamente",
    "rápido","intuitivo","productivo","constructiva","fluida","mejor","elegancia","perfectamente",
}
NEG_WORDS = {
    "lento","arruinó","congelado","no entiendo","no ayuda","desactualizada","dejó de funcionar",
    "excesivo","tardó","dolor","error","colapsando","inútil","expiró","texto plano",
    "frustrante","borró","caro","restrictiva","ambigüedades","se cae","no permite",
}

def lexicon_sentiment(text: str) -> str:
    t = normalize_text(text)
    score = 0
    for w in POS_WORDS:
        if w in t:
            score += 1
    for w in NEG_WORDS:
        if w in t:
            score -= 1
    if score > 0:
        return "pos"
    if score < 0:
        return "neg"
    return "neu"

for i in range(5):
    print(i, lexicon_sentiment(comentarios[i]), "-", comentarios[i])

#Paso 4 (principal): Clasificador supervisado Naive Bayes (NLTK)
train_data = [
    ("Me encanta que ahora se integre nativamente con Git", "pos"),
    ("El modo oscuro de la interfaz tiene un contraste excelente", "pos"),
    ("La refactorización de código se hace casi de manera mágica", "pos"),
    ("Es increíble lo fácil que es configurar un entorno virtual", "pos"),
    ("Excelente latencia en los servidores", "pos"),
    ("El autocompletado de este IDE es bastante lento", "neg"),
    ("La nueva actualización arruinó la indentación automática", "neg"),
    ("El editor se queda congelado", "neg"),
    ("No entiendo por qué quitaron el botón", "neg"),
    ("No ayuda en nada a resolver el problema", "neg"),
    ("El consumo de RAM es excesivo", "neg"),
    ("La API REST responde con un error 500", "neg"),
    ("Perdimos dos horas de producción porque el certificado SSL expiró", "neg"),
    ("El script borró accidentalmente el directorio de configuraciones", "neg"),
    ("Para esta práctica utilizaremos React en el frontend", "neu"),
    ("Se requiere una versión de Node igual o superior a la 18", "neu"),
    ("El dataset original contiene 5,000 imágenes etiquetadas", "neu"),
    ("El backup automático se ejecuta todos los días a las 3:00 AM", "neu"),
    ("El uso de CPU se mantiene estable en 45%", "neu"),
    ("El examen parcial abarcará desde el capítulo 1 hasta el 4", "neu"),
]

train_set = [(featurize(text), label) for text, label in train_data]
classifier = nltk.NaiveBayesClassifier.train(train_set)
print("Entrenamiento OK. Ejemplos:", len(train_set))    

#4.2 Predicción sobre tus textos
out_rows = []
for text in comentarios:
    feats = featurize(text)
    dist = classifier.prob_classify(feats)
    label = dist.max()
    prob = float(dist.prob(label))
    out_rows.append((text, label, prob))

out_path = "sentimientos_resultados.csv"
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["texto", "sentimiento", "probabilidad"])
    for row in out_rows:
        w.writerow(row)

print("Clasificación terminada.")
print("Archivo generado:", out_path)
print()
print("Muestra (primeros 10):")
for i, (t, lab, p) in enumerate(out_rows[:10]):
    print(f"{i:02d}  {lab}  p={p:.3f}  {t}")

#4.3 Features más informativas
classifier.show_most_informative_features(15)
    