import cv2
import numpy as np
from PIL import Image, ImageChops
import io

def perform_ela(image_bytes: bytes, quality=90) -> dict:
    """
    Performs Error Level Analysis (ELA) to detect digital tampering 
    (e.g., pasted photos or altered text layers).
    """
    try:
        original = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Resave at standard quality
        buffer = io.BytesIO()
        original.save(buffer, 'JPEG', quality=quality)
        buffer.seek(0)
        resaved = Image.open(buffer)
        
        # Calculate pixel difference
        diff = ImageChops.difference(original, resaved)
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        
        # High variance across localized blocks indicates digital tampering
        diff_arr = np.array(diff)
        tamper_detected = bool(np.std(diff_arr) > 45) # Threshold depends on testing corpus
        
        return {
            "ela_max_diff": max_diff,
            "tamper_detected": tamper_detected
        }
    except Exception as e:
        print(f"ELA Error: {e}")
        return {"ela_max_diff": 0, "tamper_detected": False}

def analyze_image(image_bytes: bytes) -> dict:
    """
    Analyzes image quality using OpenCV to flag potential issues 
    like blurriness, extreme lighting, and runs ELA for tampering detection.
    """
    try:
        # Convert the raw bytes to a format OpenCV can read
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"error": "Could not decode image"}

        # Convert to grayscale for mathematical analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Blur Detection (Variance of the Laplacian)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        is_blurry = blur_score < 100

        # 2. Brightness Check
        brightness = np.mean(gray)
        is_too_dark = brightness < 50
        is_too_bright = brightness > 220
        
        # 3. ELA Tampering Check
        ela_results = perform_ela(image_bytes)

        return {
            "blur_score": round(blur_score, 2),
            "is_blurry": bool(is_blurry),
            "brightness": round(brightness, 2),
            "is_too_dark": bool(is_too_dark),
            "is_too_bright": bool(is_too_bright),
            **ela_results # Merges the ELA dictionary into the final output
        }
    except Exception as e:
        print(f"OpenCV/Image Analysis Error: {e}")
        return {"error": str(e)}