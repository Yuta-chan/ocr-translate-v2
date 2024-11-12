from ocr_translate_annotate import extract_images_from_pdf, ocr_images_by_block, translate_text, annotate_images

# Test 1: Extract Images from PDF
print("Testing Image Extraction...")
pdf_path = "test.pdf"
image_list = extract_images_from_pdf(pdf_path)
print(f"Number of images extracted: {len(image_list)}")

# Test 2: OCR Processing
print("Testing OCR...")
ocr_results = ocr_images_by_block(image_list)
print(f"First page OCR result: {ocr_results[0]}")

# Test 3: Translation
print("Testing Translation...")
translation_results = translate_text(ocr_results)
# print(f"First page translation: {translation_results[0]}")

# Test 4: Annotating Images
print("Testing Image Annotation...")
annotated_images = annotate_images(image_list, ocr_results, translation_results)
print(f"Number of annotated images: {len(annotated_images)}")