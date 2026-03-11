import cv2
import numpy as np
import glob

# 1. Leer las rutas de las imágenes
ruta_imagenes = glob.glob('carpeta_imagenes/*.png')

for i, ruta in enumerate(ruta_imagenes):
    img = cv2.imread(ruta)
    if img is None:
        continue

    # --- CÁLCULO DEL COLOR MÁS REPETIDO ---
    # Redimensionamos un poco para que el cálculo sea más rápido 
    # (opcional, pero recomendado si las imágenes son muy grandes)
    img_pequena = cv2.resize(img, (200, 200))
    
    # Aplanamos la imagen para tener una lista de píxeles [B, G, R]
    pixeles = img_pequena.reshape(-1, 3)
    
    # Contamos las ocurrencias de cada color único
    colores, conteos = np.unique(pixeles, axis=0, return_counts=True)
    
    # Encontramos el índice del que más aparece
    indice_maximo = np.argmax(conteos)
    color_frecuente = colores[indice_maximo]
    cantidad_repeticiones = conteos[indice_maximo]
    
    # Calcular el porcentaje respecto al total de píxeles analizados
    total_pixeles_analizados = pixeles.shape[0]
    porcentaje_maximo = (cantidad_repeticiones / total_pixeles_analizados) * 100

    # --- RESULTADOS ---
    print(f"--- Imagen {i} ({ruta}) ---")
    print(f"Color que más se repite (BGR): {color_frecuente}")
    print(f"Porcentaje de este color: {porcentaje_maximo:.2f}%")
    
    # Extra: Si quieres saber si es verde, rojo, etc., basándonos en el promedio anterior
    avg_color = np.uint8(np.average(np.average(img, axis=0), axis=0))
    print(f"Color promedio general (BGR): {avg_color}")
    print("-" * 30)

    # Mostrar imagen
    cv2.imshow(f'Imagen {i}', img)
    
    # Crear un cuadrito para ver visualmente cuál es el color que más se repite
    muestra_color = np.zeros((100, 100, 3), np.uint8)
    muestra_color[:] = color_frecuente
    cv2.imshow(f'Color mas frecuente {i}', muestra_color)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

print("Proceso finalizado.")