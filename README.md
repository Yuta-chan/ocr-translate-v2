# OCR and Translation Automation: Japanese to English

This project automates the process of extracting text from PDF files in Japanese, translating it to English, and generating an annotated PDF. The workflow uses **Tesseract** and **Google Translator API** to provide an end-to-end solution for OCR and translation tasks.

## Features

- Extract images from PDF files.
- Perform Optical Character Recognition (OCR) to detect text in Japanese.
- Translate detected text to English using Google Translator API or Deep Translator.
- Annotate the original images with translations and bounding boxes.
- Generate a new annotated PDF as the output.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Yuta-chan/ocr-translation-automation.git
   cd ocr-translation-automation
   ```
2. Install the required Python dependencies:
```bash
   pip install -r requirements.txt
   ```
3. (Optional) Install Tesseract OCR:
- For Ubuntu
```bash
  sudo apt update
  sudo apt install tesseract-ocr tesseract-ocr-jpn tesseract-ocr-eng
   ```
# Usage
1. Extract Images from PDF
Run the extract_images_from_pdf() function to convert PDF pages into images.

2. Perform OCR
Use ocr_images_by_block() to detect Japanese text blocks from the images.

3. Translate Text
Translate detected text into English with translate_text().

4. Annotate Images
Use annotate_images() to overlay translations and bounding boxes onto the images.

5. Generate Annotated PDF
Save the annotated images back into a PDF using save_annotated_pdf().

## Example workflow
```bash
  from ocr_translate_annotate import (
    extract_images_from_pdf,
    ocr_images_by_block,
    translate_text,
    annotate_images,
    save_annotated_pdf
)

pdf_path = "input.pdf"
output_path = "annotated_output.pdf"

# Process PDF
image_list = extract_images_from_pdf(pdf_path)
ocr_results = ocr_images_by_block(image_list)
translation_results = translate_text(ocr_results)
annotated_images = annotate_images(image_list, ocr_results, translation_results)
save_annotated_pdf(annotated_images, output_path)
   ```
## Report
This project was developed as part of an internship. The full report comparing Tesseract and Google Cloud Vision can be found in the `judith_urbina_report.pdf` file.
