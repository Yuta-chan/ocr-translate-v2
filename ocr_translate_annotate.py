import pytesseract
from pytesseract import Output
import cv2
import fitz  # PyMuPDF
import os
from googletrans import Translator
from PIL import Image
import numpy as np

# Step 1: Extract Images from PDF
pdf_path = "test.pdf"
pdf_document = fitz.open(pdf_path)

image_list = []
for page_num in range(len(pdf_document)):
    page = pdf_document.load_page(page_num)
    pix = page.get_pixmap()  # Extract page as an image
    img_data = pix.pil_tobytes()
    image = Image.open(img_data)
    image_list.append(np.array(image))

# Step 2: OCR each image and box detection
ocr_results = []
for img in image_list:
    ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, lang="jpn")
    ocr_results.append(ocr_data)

# Step 3: Translate the detected text
translator = Translator()
translation_results = []
for ocr_data in ocr_results:
    text_translations = []
    for text in ocr_data['text']:
        if text.strip():
            translated_text = translator.translate(text, src="ja", dest="en").text
            text_translations.append(translated_text)
        else:
            text_translations.append('')
    translation_results.append(text_translations)

# Step 4: Draw annotations on the original images
annotated_images = []
for idx, img in enumerate(image_list):
    ocr_data = ocr_results[idx]
    translations = translation_results[idx]
    annotated_image = img.copy()
    for i in range(len(ocr_data['text'])):
        x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i],
                      ocr_data['width'][i], ocr_data['height'][i])
        if translations[i]:
            cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(annotated_image, translations[i], (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    annotated_images.append(annotated_image)

# Step 5: Save the results as annotated PDF
pdf_writer = fitz.open()
for img in annotated_images:
    pil_img = Image.fromarray(img)
    img_path = "temp_image.png"
    pil_img.save(img_path)
    pix = fitz.Pixmap(img_path)
    page = pdf_writer.new_page(width=pix.width, height=pix.height)
    page.insert_image((0, 0, pix.width, pix.height), filename=img_path)
    os.remove(img_path)

output_path = "output_annotated.pdf"
pdf_writer.save(output_path)

print(f"Annotated PDF saved to {output_path}")