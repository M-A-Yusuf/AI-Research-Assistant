from fastapi import APIRouter, Body
from pydantic import BaseModel
from services.summarizer import summarize_text
from typing import Optional

router = APIRouter()

class DraftRequest(BaseModel):
    section: str
    topic: str
    style: Optional[str] = None

class ProofreadRequest(BaseModel):
    text: str

@router.post("/draft_section/")
async def draft_section(req: DraftRequest):
    # Use Gemini API for LLM drafting
    prompt = f"Write a {req.section} for a paper on '{req.topic}'."
    if req.style:
        prompt += f" Use {req.style} style."
    draft = summarize_text(prompt, max_length=200, min_length=80)
    return {"draft": draft}

@router.post("/proofread/")
async def proofread(req: ProofreadRequest):
    # Use Gemini API for grammar and style proofreading
    prompt = f"Proofread and improve the grammar and style of the following academic text:\n{req.text}"
    proofread_text = summarize_text(prompt, max_length=len(req.text), min_length=int(len(req.text)*0.8))
    return {"proofread": proofread_text}
