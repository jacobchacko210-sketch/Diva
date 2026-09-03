import pytesseract
from PIL import Image
import io

# Points pytesseract to your newly installed Windows executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_bytes: bytes) -> dict:
    """
    Takes image bytes, opens them with Pillow, and extracts text using Tesseract 
    along with confidence scoring metrics.
    """
    try:
        # Convert bytes to a Pillow Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Run Tesseract with data output (word-level statistics)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        confidences = [int(c) for c in data['conf'] if int(c) != -1]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        extracted_text = " ".join([word for word in data['text'] if word.strip()])

        return {
            "text": extracted_text.strip(),
            "avg_confidence": round(avg_confidence, 2),
            "is_low_confidence": avg_confidence < 55.0
        }
        
    except Exception as e:
        print(f"OCR Error: {e}")
        return {"text": "", "avg_confidence": 0, "is_low_confidence": True}