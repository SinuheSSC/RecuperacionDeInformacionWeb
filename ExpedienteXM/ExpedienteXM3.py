import cv2
import numpy as np

# 1. Cargar evidencia_3.png y convertir a HSV
img_3 = cv2.imread('evidencia_3.png')

if img_3 is None:
    print("Error: No se encontró evidencia_3.png")
else:
    hsv_3 = cv2.cvtColor(img_3, cv2.COLOR_BGR2HSV)

    # 2. Crear máscara para el "Amarillo Pardo" (La Llave de Color)
    # Rango sugerido: Bajo [15, 100, 100], Alto [20, 255, 255]
    bajo_amarillo = np.array([15, 100, 100])
    alto_amarillo = np.array([20, 255, 255])
    mask_amarillo = cv2.inRange(hsv_3, bajo_amarillo, alto_amarillo)

    # 3. Extraer canal V (Brillo)
    # Es el canal donde se escondieron los bits (índice 2 en HSV)
    canal_v = hsv_3[:, :, 2]

    # 4. Obtener solo los píxeles que coinciden con la máscara amarilla
    # Filtramos el canal V usando la máscara como índice booleano
    pixeles_clave = canal_v[mask_amarillo == 255]

    # 5. Aplicar decodificación LSB a ese subconjunto
    bits_extraidos = [p & 1 for p in pixeles_clave]

    mensaje_final = ""
    for i in range(0, len(bits_extraidos), 8):
        byte = bits_extraidos[i:i+8]
        if len(byte) < 8: break
        
        # Convertir bits a carácter ASCII
        char_code = int("".join(map(str, byte)), 2)
        caracter = chr(char_code)
        mensaje_final += caracter
        
        # Detenerse al encontrar el delimitador
        if "###FIN###" in mensaje_final:
            break

    # 6. Reportar hallazgos
    print("--- RESULTADO DE LA MISIÓN 3 ---")
    print("Mensaje Recuperado:", mensaje_final.replace("###FIN###", ""))
    
    # Opcional: ver qué partes de la imagen fueron procesadas
    cv2.imshow('Zonas de la Llave Amarilla', mask_amarillo)
    cv2.waitKey(0)
    cv2.destroyAllWindows()