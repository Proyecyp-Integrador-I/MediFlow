from pdf2image import convert_from_path
import cv2
import numpy as np
import pytesseract

# Especificar la ruta de Tesseract si estás en Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def pdf_to_images(pdf_path):
    """Convierte las páginas del PDF a imágenes."""
    images = convert_from_path(pdf_path)
    return images

def preprocess_and_crop_image(image):
    """Detecta los bordes de la tabla y recorta la imagen para enfocarse en ella."""
    img_array = np.array(image)

    edges = cv2.Canny(img_array, 50, 150, apertureSize=3)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    table_contour = max(contours, key=cv2.contourArea)

    x, y, w, h = cv2.boundingRect(table_contour)
    cropped_image = img_array[y:y+h, x:x+w]

    return cropped_image

def extract_text_from_image(image):
    """Aplica OCR a la imagen recortada."""
    text = pytesseract.image_to_string(image)
    return text

def process_pdf(pdf_path):
    """Procesa el PDF y realiza OCR en la tabla recortada."""
    images = pdf_to_images(pdf_path)
    ocr_results = []

    for image in images:
        # Preprocesar y recortar la imagen para enfocar la tabla
        cropped_image = preprocess_and_crop_image(image)
        
        # Extraer texto mediante OCR
        text = extract_text_from_image(cropped_image)
        ocr_results.append(text)

    return ocr_results