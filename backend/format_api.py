from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

router = APIRouter()

class FormatRequest(BaseModel):
    text: str
    style: Literal["IEEE", "ACM", "APA", "MLA"]

@router.post("/format_draft/")
async def format_draft(req: FormatRequest):
    # Demo: just wrap text in style tags (replace with real formatting logic)
    if req.style == "IEEE":
        formatted = f"[IEEE FORMAT]\n{req.text}"
    elif req.style == "ACM":
        formatted = f"[ACM FORMAT]\n{req.text}"
    elif req.style == "APA":
        formatted = f"[APA FORMAT]\n{req.text}"
    elif req.style == "MLA":
        formatted = f"[MLA FORMAT]\n{req.text}"
    else:
        formatted = req.text
    return {"formatted": formatted}
