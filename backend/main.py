
"""
====================================
  Proofessor: AI-Powered Research Assistant
====================================
One-stop AI platform for academia: Summarize, review, and co-author research papers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router as api_router
from coauthor_api import router as coauthor_router
from plagiarism_api import router as plagiarism_router
from format_api import router as format_router
from version_api import router as version_router
from comments_api import router as comments_router
from export_api import router as export_router

 

app = FastAPI(title="Proofessor", description="AI-Powered Research Assistant Backend")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Proofessor Backend Running"}

# Include routers
app.include_router(api_router)
app.include_router(coauthor_router)
app.include_router(plagiarism_router)
app.include_router(format_router)
app.include_router(version_router)
app.include_router(comments_router)
app.include_router(export_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)