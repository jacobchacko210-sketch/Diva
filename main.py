from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from ocr import extract_text_from_image
from image_analysis import analyze_image
from qr_verification import verify_qr
from metadata import extract_metadata
from fraud_engine import calculate_risk_score
from llm_explanation import generate_explanation
from chatbot import get_chatbot_response
from register import router as register_router
from login import router as login_router
app = FastAPI()

app.include_router(register_router)
app.include_router(login_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    document_context: Optional[dict] = None

@app.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    file_bytes = await file.read()
    
    # 1. Run all analysis modules
    ocr_result = extract_text_from_image(file_bytes)
    image_data = analyze_image(file_bytes)
    qr_data = verify_qr(file_bytes)
    meta_data = extract_metadata(file_bytes)
    
    # 2. Extract plain text string for frontend and chat context
    plain_text = ocr_result.get("text", "") if isinstance(ocr_result, dict) else str(ocr_result)

    # 3. Calculate fraud risk
    fraud_results = calculate_risk_score(
        extracted_text=ocr_result, 
        image_data=image_data, 
        qr_data=qr_data, 
        meta_data=meta_data
    )
    
    # 4. Generate summary explanation
    explanation = generate_explanation(
        risk_score=fraud_results["final_score"], 
        flags=fraud_results["flags"]
    )
        
    return {
        "filename": file.filename,
        "risk_score": fraud_results["final_score"],
        "flags": fraud_results["flags"],
        "explanation": explanation,
        "metadata_analysis": meta_data,
        "image_analysis": image_data,
        "qr_verification": qr_data,
        "extracted_text": plain_text,  # Returns plain string to prevent React rendering errors
        "ocr_metrics": ocr_result if isinstance(ocr_result, dict) else {},
        "message": "Document analyzed successfully!"
    }

@app.post("/chat/")
async def chat_with_assistant(request: ChatRequest):
    reply = get_chatbot_response(
        user_message=request.message, 
        document_context=request.document_context
    )
    return {"reply": reply}