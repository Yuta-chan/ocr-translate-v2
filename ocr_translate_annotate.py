import pytesseract
from pytesseract import Output
import cv2
import fitz  # PyMuPDF
import os
# from googletrans import Translator does not work sometimes
from deep_translator import GoogleTranslator
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import requests

# Function to download the font automatically if not present
def download_japanese_font(font_url, font_filename):
    font_path = os.path.join(os.getcwd(), font_filename)
    if not os.path.exists(font_path):
        print("Font not found locally. Downloading font...")
        try:
            response = requests.get(font_url, stream=True)
            response.raise_for_status()  # Raise an error for bad responses
            with open(font_path, 'wb') as font_file:
                for chunk in response.iter_content(chunk_size=8192):
                    font_file.write(chunk)
            print("Font downloaded successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading the font: {e}")
            font_path = None
    return font_path

# Step 1: Extract Images from PDF
def extract_images_from_pdf(pdf_path):
    import fitz  # PyMuPDF
    from PIL import Image
    import numpy as np

    pdf_document = fitz.open(pdf_path)
    image_list = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()  # Extract page as an image
        img_data = pix.samples
        image = Image.frombytes("RGB", [pix.width, pix.height], img_data)
        image_list.append(np.array(image))

    return image_list

# Step 2: OCR each image and box detection
def ocr_images_by_block(image_list):
    import pytesseract
    from pytesseract import Output

    ocr_results = []

    for img in image_list:
        # Use pytesseract to get block-level data
        ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, lang="jpn")

        grouped_blocks = []  # To store grouped text by blocks
        current_block = -1
        block_text = ""

        for i in range(len(ocr_data['text'])):
            if ocr_data['text'][i].strip():  # Ignore empty text
                if ocr_data['block_num'][i] != current_block:
                    # If we're on a new block, save the previous block text and start a new one
                    if block_text:
                        grouped_blocks.append(block_text.strip())
                    block_text = ocr_data['text'][i]
                    current_block = ocr_data['block_num'][i]
                else:
                    # If still on the same block, keep adding text
                    block_text += " " + ocr_data['text'][i]

        # Add the last block if present
        if block_text:
            grouped_blocks.append(block_text.strip())

        ocr_results.append(grouped_blocks)

    return ocr_results

# Step 3: Translate the detected text
from deep_translator import GoogleTranslator

def translate_text(ocr_results):
    translator = GoogleTranslator(source='ja', target='en')
    translation_results = []

    for blocks in ocr_results:
        block_translations = []
        for block in blocks:
            if block.strip():
                translated_block = translator.translate(block)
                block_translations.append(translated_block)
            else:
                block_translations.append('')
        translation_results.append(block_translations)

    return translation_results

def annotate_images(image_list, ocr_results, translation_results, font_path="NotoSansCJKjp-Regular.ttf"):
    annotated_images = []
    
    # Load the font that supports Japanese characters
    try:
        font = ImageFont.truetype(font_path, 20)  # Font size is 20pt, adjust as needed
    except IOError:
        print(f"Could not load the font file at: {font_path}. Please check the path.")
        return annotated_images

    # Iterate through each image and its corresponding OCR results and translations
    for idx, img in enumerate(image_list):
        ocr_data = ocr_results[idx]  # `ocr_data` is a dictionary
        translations = translation_results[idx]
        
        # Convert the image to a Pillow Image object
        annotated_image = Image.fromarray(img)
        draw = ImageDraw.Draw(annotated_image)

        current_block = -1
        block_coords = []

        # Iterate over the text elements in OCR data
        num_elements = len(ocr_data['text'])
        for i in range(num_elements):
            if ocr_data['text'][i].strip():  # If text is not empty
                # Check if the current block is different from the previous block
                if ocr_data['block_num'][i] != current_block:
                    # Draw the previous block bounding box if it exists
                    if block_coords:
                        draw.rectangle(block_coords, outline="green", width=2)
                    # Start a new block
                    current_block = ocr_data['block_num'][i]
                    block_coords = [
                        (ocr_data['left'][i], ocr_data['top'][i]),
                        (ocr_data['left'][i] + ocr_data['width'][i], ocr_data['top'][i] + ocr_data['height'][i])
                    ]
                else:
                    # Expand the bounding box for the current block
                    block_coords[1] = (
                        max(block_coords[1][0], ocr_data['left'][i] + ocr_data['width'][i]),
                        max(block_coords[1][1], ocr_data['top'][i] + ocr_data['height'][i])
                    )
        
        # Draw the final block if any
        if block_coords:
            draw.rectangle(block_coords, outline="green", width=2)

        # Annotate with translated text for each block
        for i, translated_text in enumerate(translations):
            if translated_text.strip():
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                draw.text((x, y - 20), translated_text, font=font, fill="red")

        # Convert the annotated image back to a NumPy array
        annotated_images.append(np.array(annotated_image))

    return annotated_images

# Step 5: Save the results as annotated PDF
def save_annotated_pdf(annotated_images, output_path):
    pdf_writer = fitz.open()
    for img in annotated_images:
        pil_img = Image.fromarray(img)
        img_path = "temp_image.png"  # Ensure we use the .png extension, which is supported by PIL
        pil_img.save(img_path, format="PNG")  # Save with a defined extension (e.g., PNG)
        pix = fitz.Pixmap(img_path)
        page = pdf_writer.new_page(width=pix.width, height=pix.height)
        page.insert_image((0, 0, pix.width, pix.height), filename=img_path)
        os.remove(img_path)
    pdf_writer.save(output_path)
    print(f"Annotated PDF saved to {output_path}")

# Main Execution
if __name__ == "__main__":
    pdf_path = "test.pdf"
    output_path = "output_annotated.pdf"
    font_url = "https://github.com/minoryorg/Noto-Sans-CJK-JP/blob/master/fonts/NotoSansCJKjp-Regular.ttf?raw=true"
    font_filename = "NotoSansCJKjp-Regular.ttf"

    # Step 1: Download the font
    font_path = download_japanese_font(font_url, font_filename)

    # Step 2: Extract Images
    image_list = extract_images_from_pdf(pdf_path)
    
    # Step 3: Perform OCR
    # ocr_results = ocr_images(image_list)
    
    # Step 4: Translate Text
    translation_results = translate_text(ocr_results)
    
    # Step 5: Annotate Images
    annotated_images = annotate_images(image_list, ocr_results, translation_results, font_path)
    
    # Step 6: Save Annotated PDF
    save_annotated_pdf(annotated_images, output_path)