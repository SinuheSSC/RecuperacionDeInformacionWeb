import cv2
import numpy as np

# 1. Cargar la imagen interceptada
# Asegúrate de que el archivo 'evidencia_2.png' esté en la misma carpeta
img = cv2.imread('evidencia_2.png')

if img is None:
    print("Error: No se encontró el archivo evidencia_2.png")
else:
    # 2. Convertir de BGR (formato estándar de OpenCV) a HSV
    # El espacio HSV es ideal para filtrar colores porque separa el Matiz (H)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 3. Definir el rango de la "Tinta Camaleón"
    # Las pistas indican que la tinta está cerca de H=64.
    # El formato en cv2.inRange es (H, S, V)
    # Usamos 0 y 255 en S y V para que no importe qué tan saturado o brillante sea.
    rango_bajo = np.array([60, 0, 0])
    rango_alto = np.array([66, 255, 255])

    # 4. Crear la máscara para revelar el mensaje
    # Esta función pone en BLANCO los píxeles en el rango y en NEGRO el resto.
    mascara = cv2.inRange(hsv, rango_bajo, rango_alto)

    # 5. Mostrar los resultados
    cv2.imshow('Imagen Original (Fondo Verde)', img)
    cv2.imshow('Mensaje Revelado (Filtro HSV)', mascara)
    
    print("Misión 2: Buscando el mensaje en la ventana de imagen...")
    
    # Esperar a que se presione una tecla para cerrar las ventanas
    cv2.waitKey(0)
    cv2.destroyAllWindows()