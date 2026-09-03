from PIL import Image, ExifTags
import io

def extract_metadata(image_bytes: bytes) -> dict:
    """
    Extracts EXIF metadata from the image to check for signs of tampering,
    such as the use of photo editing software.
    """
    try:
        # Open the image using Pillow
        image = Image.open(io.BytesIO(image_bytes))
        
        # Check if the image format supports EXIF (usually JPEGs and TIFFs)
        if not hasattr(image, '_getexif') or image._getexif() is None:
            return {
                "has_metadata": False, 
                "suspicious_software": False, 
                "message": "No EXIF metadata found."
            }
            
        exif_data = image._getexif()
        suspicious_software = False
        software_used = "Unknown"
        creation_date = "Unknown"
        
        # Loop through metadata tags
        for tag_id, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            
            # Clean up byte values for readability
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8')
                except UnicodeDecodeError:
                    value = str(value)
            
            # Check for suspicious editing software
            if tag_name == 'Software' and isinstance(value, str):
                software_used = value
                if 'photoshop' in value.lower() or 'gimp' in value.lower():
                    suspicious_software = True
                    
            if tag_name == 'DateTime':
                creation_date = value
                    
        return {
            "has_metadata": True,
            "suspicious_software": suspicious_software,
            "software_used": software_used,
            "creation_date": creation_date
        }
        
    except Exception as e:
        print(f"Metadata Error: {e}")
        return {"has_metadata": False, "suspicious_software": False, "error": str(e)}