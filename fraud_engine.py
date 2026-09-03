import re
from datetime import datetime

INDIAN_DOC_KEYWORDS = [
    "GOVERNMENT OF INDIA", "INCOME TAX", "AADHAAR", 
    "ELECTION COMMISSION", "TRANSPORT DEPARTMENT", "PAN", "REPUBLIC OF INDIA"
]

def calculate_risk_score(extracted_text, image_data: dict, qr_data: dict, meta_data: dict) -> dict:
    """
    Evaluates the evidence from all modules to generate a combined fraud risk score
    and a list of specific warning flags[cite: 11].
    """
    risk_score = 0
    flags = []

    # 1. Normalize OCR input (handles either dict or string)
    if isinstance(extracted_text, dict):
        raw_text = extracted_text.get("text", "")
        is_low_confidence = extracted_text.get("is_low_confidence", False)
        avg_confidence = extracted_text.get("avg_confidence", 100)
    else:
        raw_text = str(extracted_text or "")
        is_low_confidence = False
        avg_confidence = 100

    text_upper = raw_text.upper()

    # 2. OCR Confidence Check
    if is_low_confidence:
        risk_score += 35
        flags.append(f"Low OCR confidence ({avg_confidence}%): Altered or distorted text detected")

    # 3. Document Type Classification
    if text_upper.strip() and not any(keyword in text_upper for keyword in INDIAN_DOC_KEYWORDS):
        risk_score += 80
        flags.append("Unrecognized/Non-Indian document type detected")

    # 4. Text Presence
    if not raw_text.strip():
        risk_score += 50
        flags.append("No text detected")
    elif len(raw_text.strip()) < 15:
        risk_score += 40
        flags.append("Insufficient text extracted")

    # 5. Logical Validation (Dates & Demographics)
    date_pattern = r'(\d{2}/\d{2}/\d{4})'
    dates = re.findall(date_pattern, raw_text)
    if len(dates) >= 2:
        try:
            d1 = datetime.strptime(dates[0], "%m/%d/%Y")
            d2 = datetime.strptime(dates[1], "%m/%d/%Y")
            if d2 < d1:
                risk_score += 60
                flags.append("Invalid date sequence detected")
        except ValueError:
            pass

    if "SEX F" in text_upper and any(m in text_upper for m in ["MICHAEL", "JOHN", "DAVID"]):
        risk_score += 70
        flags.append("Demographic discrepancy: Potential name-to-gender mismatch")

    # 6. Image Quality & Tampering Checks
    if image_data.get("is_blurry"):
        risk_score += 30
        flags.append("Image is heavily blurred")
        
    if image_data.get("is_too_dark") or image_data.get("is_too_bright"):
        risk_score += 20
        flags.append("Poor lighting conditions")

    if image_data.get("tamper_detected"):
        risk_score += 60
        flags.append("ELA Anomaly: Digital image editing or splicing detected")
        
    # 7. QR Verification Checks
    if not qr_data.get("qr_found"):
        risk_score += 30
        flags.append("Missing or unreadable QR code")
    else:
        flags.append("Valid QR Code Found")

    # 8. Metadata Checks
    if meta_data.get("suspicious_software"):
        risk_score += 80
        flags.append(f"Edited with: {meta_data.get('software_used')}")
    elif not meta_data.get("has_metadata"):
        risk_score += 15
        flags.append("Missing EXIF Metadata (Possible screenshot or social media download)")

    # Cap risk score at 100
    risk_score = min(risk_score, 100)
    
    return {
        "final_score": risk_score,
        "flags": flags
    }