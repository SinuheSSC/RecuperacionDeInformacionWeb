import cv2
import numpy as np

# 1. Cargar la imagen en escala de grises
img = cv2.imread('evidencia_1.png', cv2.IMREAD_GRAYSCALE)

# 2. Aplanar la imagen (convertir matriz a una lista larga de píxeles)
pixels = img.flatten()

# 3. Extraer el bit menos significativo de cada píxel
bits = [p & 1 for p in pixels]

# 4. Agrupar bits en bytes (8 bits) y convertir a caracteres
mensaje = ""
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    if len(byte) < 8: break
    
    # Convertir lista de bits a un entero
    char_code = int("".join(map(str, byte)), 2)
    caracter = chr(char_code)
    mensaje += caracter
    
    # Detenerse si encontramos la palabra clave
    if "###FIN###" in mensaje:
        break

print("Mensaje Recuperado (Misión 1):", mensaje.replace("###FIN###", ""))