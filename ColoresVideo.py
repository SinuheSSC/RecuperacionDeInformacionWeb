import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)
i = 0

while(True):
    ret, img = cap.read()
    if ret:
        # 1. Mostrar el video y guardar (tu código original)
        cv.imshow('video', img)
        cv.imwrite(r'E:\Mi_Usuario\Documents\RecuperacionWeb\capturasVideo' + '\\' + str(i) + '.jpg', img)
        i += 1

        # 2. CALCULAR COLOR PREDOMINANTE
        # Reducimos la imagen para que el proceso sea rápido
        img_pequena = cv.resize(img, (100, 100))
        # Aplanamos la imagen a una lista de colores [B, G, R]
        pixeles = img_pequena.reshape(-1, 3)
        
        # Convertimos a tuplas para poder contarlos
        colores, conteos = np.unique(pixeles, axis=0, return_counts=True)
        
        # Buscamos el índice del color que más se repite
        indice_max = np.argmax(conteos)
        color_ganador = colores[indice_max]
        repeticiones = conteos[indice_max]
        
        # 3. CALCULAR PORCENTAJE
        porcentaje = (repeticiones / len(pixeles)) * 100
        
        # Imprimir resultados en consola (B, G, R)
        # Nota: OpenCV usa Blue, Green, Red en ese orden
        print(f"Frame {i}: Color BGR {color_ganador} - Frecuencia: {porcentaje:.2f}%")

        k = cv.waitKey(1) & 0xFF
        if k == 27:
            break
    else:
        break

cap.release()
cv.destroyAllWindows()