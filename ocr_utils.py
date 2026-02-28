import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np

def preprocess_image(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return gray

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    processed = preprocess_image(image)
    text = pytesseract.image_to_string(processed)
    return text

def extract_text_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    full_text = ""
    for page in pages:
        processed = preprocess_image(page)
        text = pytesseract.image_to_string(processed)
        full_text += text + "\n"
    return full_text