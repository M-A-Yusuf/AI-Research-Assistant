from fastapi import APIRouter, Body
from pydantic import BaseModel
import os
import json
from typing import List
from dotenv import load_dotenv

load_dotenv()

COMMENTS_FILE = os.getenv("COMMENTS_FILE", "comments.json")
if not os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "w") as f:
        json.dump([], f)

router = APIRouter()

class Comment(BaseModel):
    user: str
    text: str

@router.post("/add_comment/")
async def add_comment(comment: Comment):
    with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
        comments = json.load(f)
    comments.append(comment.dict())
    with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(comments, f)
    return {"status": "added"}

@router.get("/get_comments/")
async def get_comments():
    with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
        comments = json.load(f)
    return {"comments": comments}
