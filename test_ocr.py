import pytesseract
from PIL import Image

text = pytesseract.image_to_string(Image.open("sample_report.png"))
print(text)