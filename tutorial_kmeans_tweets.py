from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# --- 1. Tweets de ejemplo ---
tweets = [
    # Deportes
    "Gran partido de fútbol ayer, el gol fue increíble",
    "El equipo ganó la liga, qué temporada tan buena",
    "Messi anotó un golazo en el último minuto",
    "La selección entrena para el mundial de fútbol",
    "Increíble jugada del portero, atajó todo",
    "El clásico del domingo fue muy emocionante",

    # Tecnología
    "Acabo de comprar el nuevo iPhone, la cámara es genial",
    "Python es el mejor lenguaje para aprender a programar",
    "La inteligencia artificial va a cambiar todo",
    "Actualizé mi laptop y ahora va mucho más rápido",
    "El nuevo procesador tiene un rendimiento increíble",
    "Aprendiendo machine learning con scikit-learn",

    # Comida
    "Las tacos de pastor de aquí son los mejores",
    "Hoy cociné una pasta con salsa de tomate casera",
    "El café de esta mañana estaba delicioso",
    "Probé un restaurante nuevo y la pizza estaba buenísima",
    "Nada como unos chilaquiles para desayunar",
    "Receta fácil: arroz con pollo y verduras",

    # Familia
    "Pasamos un día increíble en el parque con los niños",
    "Mi hermana se casó el fin de semana pasado, fue hermoso",
    "Los abuelos vinieron a visitarnos, qué alegría",
    "Celebramos el cumpleaños de mi hijo con una gran fiesta",
    "Mi mamá cocina el mejor pastel de chocolate",
]

# --- 2. Vectorizar los tweets con TF-IDF ---
vectorizador = TfidfVectorizer(
    stop_words=None,       # podríamos filtrar stopwords del español
    max_features=100,      # usar las 100 palabras más relevantes
    lowercase=True,        # todo a minúsculas
)
X = vectorizador.fit_transform(tweets)

print(f"Matriz TF-IDF: {X.shape[0]} tweets × {X.shape[1]} palabras")

# --- 3. Aplicar K-Means ---
k = 4  # queremos 3 grupos
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
kmeans.fit(X)

etiquetas = kmeans.labels_  # a qué cluster pertenece cada tweet

# --- 4. Mostrar resultados ---
for cluster_id in range(k):
    print(f"\n{'='*50}")
    print(f"  CLUSTER {cluster_id}")
    print(f"{'='*50}")
    for i, tweet in enumerate(tweets):
        if etiquetas[i] == cluster_id:
            print(f"  • {tweet}")

# --- 5. Palabras clave de cada cluster ---
print(f"\n{'='*50}")
print("  PALABRAS CLAVE POR CLUSTER")
print(f"{'='*50}")
nombres_palabras = vectorizador.get_feature_names_out()
centroides = kmeans.cluster_centers_

for cluster_id in range(k):
    # Obtener las 5 palabras con mayor peso en el centroide
    indices_top = centroides[cluster_id].argsort()[-5:][::-1]
    palabras_top = [nombres_palabras[i] for i in indices_top]
    print(f"  Cluster {cluster_id}: {', '.join(palabras_top)}")

# --- 6. Graficar (reducción a 2D con SVD) ---
from sklearn.decomposition import TruncatedSVD

svd = TruncatedSVD(n_components=2, random_state=42)
X_2d = svd.fit_transform(X)

colores = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6']  # colores para hasta 6 clusters
nombres_cluster = [f'Cluster {i}' for i in range(k)]

plt.figure(figsize=(10, 6))
for cluster_id in range(k):
    mask = etiquetas == cluster_id
    plt.scatter(
        X_2d[mask, 0], X_2d[mask, 1],
        c=colores[cluster_id],
        label=nombres_cluster[cluster_id],
        s=100, alpha=0.7, edgecolors='black'
    )
    for i in range(len(tweets)):
        if etiquetas[i] == cluster_id:
            plt.annotate(
                tweets[i][:25] + "...",
                (X_2d[i, 0], X_2d[i, 1]),
                fontsize=7, alpha=0.8
            )

plt.title("Agrupación de Tweets con K-Means")
plt.xlabel("Componente 1")
plt.ylabel("Componente 2")
plt.legend()
plt.tight_layout()
plt.savefig("kmeans_tweets.png", dpi=150)
plt.show()
print("\nGráfica guardada en kmeans_tweets.png")