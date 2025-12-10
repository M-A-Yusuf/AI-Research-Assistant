

from fastapi import APIRouter, UploadFile, File, Form
from services.pdf_utils import extract_text_from_pdf
from services.summarizer import summarize_text
from services.citations import extract_citations
import os
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/summarize/")
async def summarize(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    text = extract_text_from_pdf(file_path)
    # Use Gemini API for summarization
    summary = summarize_text(text)
    return {"summary": summary}

@router.post("/citations/")
async def citations(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    text = extract_text_from_pdf(file_path)
    citations = extract_citations(text)
    return citations