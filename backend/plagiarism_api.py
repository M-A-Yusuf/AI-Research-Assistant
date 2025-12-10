
from fastapi import APIRouter, UploadFile, File, Form
from typing import List
import os
from services.pdf_utils import extract_text_from_pdf
from collections import Counter
import re
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

def ngram_overlap(text1, text2, n=5):
    def ngrams(text, n):
        words = re.findall(r"\w+", text.lower())
        return [tuple(words[i:i+n]) for i in range(len(words)-n+1)]
    ngrams1 = Counter(ngrams(text1, n))
    ngrams2 = Counter(ngrams(text2, n))
    overlap = sum((ngrams1 & ngrams2).values())
    total = sum(ngrams1.values())
    return overlap / total if total > 0 else 0

@router.post("/plagiarism_check/")
async def plagiarism_check(
    file: UploadFile = File(...),
    draft: str = Form(...)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    paper_text = extract_text_from_pdf(file_path)
    overlap = ngram_overlap(paper_text, draft)
    return {"overlap": overlap}
