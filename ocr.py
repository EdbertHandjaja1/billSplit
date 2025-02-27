from PIL import Image
import pytesseract
import numpy as np

def extract_text_from_image(filename):
    """Extracts text from an image using OCR (Tesseract)."""
    img = np.array(Image.open(filename))
    text = pytesseract.image_to_string(img)
    return text.strip()

if __name__ == "__main__":
    filename = "example_bill.jpg"  # Change to your receipt image
    extracted_text = extract_text_from_image(filename)
    
    # Save extracted text to a file
    with open("extracted_text.txt", "w") as f:
        f.write(extracted_text)

    print("OCR extraction complete. Saved to extracted_text.txt")
