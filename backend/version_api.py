from fastapi import APIRouter, Body
from pydantic import BaseModel
import os
import json
from typing import List
from dotenv import load_dotenv

load_dotenv()

VERSIONS_DIR = os.getenv("VERSIONS_DIR", "draft_versions")
os.makedirs(VERSIONS_DIR, exist_ok=True)

router = APIRouter()

class SaveDraftRequest(BaseModel):
    draft: str
    name: str

@router.post("/save_draft/")
async def save_draft(req: SaveDraftRequest):
    path = os.path.join(VERSIONS_DIR, f"{req.name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"draft": req.draft}, f)
    return {"status": "saved", "name": req.name}

@router.get("/list_drafts/")
async def list_drafts():
    files = [f[:-5] for f in os.listdir(VERSIONS_DIR) if f.endswith(".json")]
    return {"drafts": files}

@router.get("/get_draft/{name}")
async def get_draft(name: str):
    path = os.path.join(VERSIONS_DIR, f"{name}.json")
    if not os.path.exists(path):
        return {"error": "not found"}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"draft": data["draft"]}
