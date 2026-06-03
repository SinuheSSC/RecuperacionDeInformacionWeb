# Algoritmos de Aprendizaje Automático
**Alumno:** Sinuhe Sánchez Contreras  
**Materia:** Recuperación de Información en la Web 

## 1. Aprendizaje Supervisado
*Requiere un conjunto de datos de entrenamiento con etiquetas (respuestas conocidas).*

* **Regresión Lineal:** Utilizado para predecir un valor numérico continuo. Es ideal para estimar tendencias de mercado o precios de propiedades.
* **Regresión Logística:** A pesar de su nombre, se usa para clasificación (usualmente binaria). Determina la probabilidad de que un elemento pertenezca a una clase (ej. Sí/No).
* **Árboles de Decisión:** Modelos en forma de diagrama de flujo que toman decisiones basadas en reglas de "si-entonces" sobre las características de los datos.
* **Random Forest (Bosques Aleatorios):** Una combinación de múltiples árboles de decisión que trabajan juntos para obtener una predicción más precisa y estable.
* **Máquinas de Vectores de Soporte (SVM):** Encuentra el mejor hiperplano para separar diferentes clases en un espacio de múltiples dimensiones.

---

## 2. Aprendizaje No Supervisado
*El algoritmo busca patrones o estructuras ocultas en datos que no tienen etiquetas.*

* **K-Means (K-Medias):** Agrupa los datos en "K" grupos (clusters) basándose en la distancia y similitud entre los puntos.
* **PCA (Análisis de Componentes Principales):** Reduce la complejidad de los datos (dimensionalidad) manteniendo la mayor cantidad de información posible.
* **DBSCAN:** Un algoritmo de agrupamiento basado en la densidad, capaz de identificar grupos de formas irregulares y detectar puntos de ruido (anomalías).
* **Algoritmo Apriori:** Utilizado para el aprendizaje de reglas de asociación. Es el clásico algoritmo detrás de "quienes compraron esto, también compraron aquello".
* **Agrupamiento Jerárquico:** Crea una jerarquía de clusters que se puede visualizar en un diagrama llamado dendrograma.

---

## 3. Aprendizaje Semi-supervisado
*Utiliza una pequeña cantidad de datos etiquetados para guiar el aprendizaje sobre una gran masa de datos sin etiquetar.*

* **Self-Training (Auto-entrenamiento):** El modelo se entrena con los pocos datos etiquetados y predice etiquetas para los no etiquetados; las predicciones más seguras se reincorporan al entrenamiento.
* **Propagación de Etiquetas (Label Propagation):** Modela los datos como un grafo donde las etiquetas "fluyen" desde los nodos conocidos hacia sus vecinos más cercanos.
* **Co-Training (Co-entrenamiento):** Requiere que los datos tengan dos "vistas" o características independientes. Dos modelos se entrenan por separado y se proporcionan etiquetas mutuamente.
* **S3VM (SVM Semi-supervisado):** Extiende la lógica de las máquinas de vectores de soporte para incluir datos no etiquetados en la búsqueda del margen de separación óptimo.
* **Redes Generativas Antagónicas (GANs):** En entornos semi-supervisados, el discriminador de la red se entrena para clasificar datos reales en categorías específicas usando muy pocas muestras etiquetadas.

---

## Resumen de Uso
| Tipo | ¿Cuándo usarlo? |
| :--- | :--- |
| **Supervisado** | Cuando conoces el resultado deseado y tienes ejemplos previos etiquetados. |
| **No Supervisado** | Cuando quieres explorar los datos y encontrar grupos o relaciones desconocidas. |
| **Semi-supervisado** | Cuando etiquetar datos es muy costoso o requiere mucho tiempo humano. |