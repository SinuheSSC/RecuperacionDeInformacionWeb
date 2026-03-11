import cv2
import numpy as np

# Leer la imagen
img = cv2.imread('frutas.png')

# 1. Obtener dimensiones totales
alto, ancho = img.shape[:2]
total_pixeles = alto * ancho

# Convertir la imagen al espacio de color HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Definir el rango para detectar verde
lower_green = np.array([35, 100, 100])
upper_green = np.array([85, 255, 255])

# Crear la máscara
mask = cv2.inRange(hsv, lower_green, upper_green)

# --- CÁLCULO DEL PORCENTAJE ---
# Contamos cuántos píxeles en la máscara son blancos (valor 255)
pixeles_verdes = cv2.countNonZero(mask)

# Sacamos el porcentaje
porcentaje_verde = (pixeles_verdes / total_pixeles) * 100
# ------------------------------

# Aplicar la máscara a la imagen original
result = cv2.bitwise_and(img, img, mask=mask)

print(f"Píxeles totales: {total_pixeles}")
print(f"Píxeles verdes detectados: {pixeles_verdes}")
print(f"Porcentaje de color verde: {porcentaje_verde:.2f}%")

# Mostrar resultados
cv2.imshow("Imagen Original", img)
cv2.imshow("Mascara (Blanco = Verde)", mask) # Te ayuda a ver qué está contando
cv2.imshow("Resultado Final", result)
cv2.waitKey(0)
cv2.destroyAllWindows()