import cv2
import numpy as np

def verify_qr(image_bytes: bytes) -> dict:
    """
    Detects and decodes QR codes in the document image using OpenCV.
    """
    try:
        # Convert bytes to numpy array and decode to image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"error": "Could not decode image", "qr_found": False}

        # Initialize OpenCV's QR code detector
        detector = cv2.QRCodeDetector()
        
        # Detect and decode the QR code
        data, bbox, _ = detector.detectAndDecode(img)

        # If data exists, a QR code was successfully read
        if data:
            return {
                "qr_found": True,
                "qr_data": data,
                "message": "QR code successfully decoded."
            }
        else:
            return {
                "qr_found": False,
                "qr_data": None,
                "message": "No readable QR code found in the image."
            }
            
    except Exception as e:
        print(f"QR Verification Error: {e}")
        return {"error": str(e), "qr_found": False}