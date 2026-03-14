import pytesseract
from PIL import Image
import io
import re

# IMPORTANT: You may need to set the tesseract_cmd path if it's not in your system PATH
# For Windows, uncomment and adjust the line below if Tesseract is installed locally:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_document(file_bytes: bytes) -> dict:
    """
    Takes an image file as bytes, runs OCR to extract text,
    and performs basic heuristic checks to identify the document type.
    """
    try:
        # Load image from bytes
        image = Image.open(io.BytesIO(file_bytes))
        
        # Extract text using Tesseract
        raw_text = pytesseract.image_to_string(image)
        text_lower = raw_text.lower()
        
        # --- Heuristic Analysis for MVP ---
        document_type = "Unknown Document"
        confidence_score = 0
        extracted_data = {}
        
        # 1. Income Certificate Check
        if "income" in text_lower and ("certificate" in text_lower or "praman patra" in text_lower):
            document_type = "Income Certificate"
            confidence_score = 85
            # Basic attempt to find an income number (looking for 'Rs', 'INR', or digits near 'income')
            income_match = re.search(r'(?:rs\.?|inr|rupees|₹)?\s*([\d,]+(?:\.\d{2})?)', raw_text, re.IGNORECASE)
            if income_match:
                 extracted_data['detected_income'] = income_match.group(1).replace(',', '')

        # 2. Caste Certificate Check
        elif "caste" in text_lower or "tribe" in text_lower or "backward class" in text_lower:
            document_type = "Caste Certificate"
            confidence_score = 85
            # Look for common category keywords
            if "sc " in text_lower or "scheduled caste" in text_lower:
                extracted_data['detected_category'] = "SC"
            elif "st " in text_lower or "scheduled tribe" in text_lower:
                extracted_data['detected_category'] = "ST"
            elif "obc" in text_lower:
                extracted_data['detected_category'] = "OBC"

        # 3. Marksheet / Education Check
        elif "marksheet" in text_lower or "board of secondary education" in text_lower or "university" in text_lower:
            document_type = "Education Marksheet"
            confidence_score = 75
            
        return {
            "status": "success",
            "document_type": document_type,
            "confidence_score": confidence_score,
            "raw_text_snippet": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
            "extracted_data": extracted_data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
