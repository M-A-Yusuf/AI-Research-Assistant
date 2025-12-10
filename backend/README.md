# Proofessor Backend

## Setup
1. Copy `.env.example` to `.env` and fill in your Gemini API key and other secrets.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints
- `/summarize/` (POST): Summarize uploaded PDF
- `/draft_section/` (POST): AI co-author drafting
- `/proofread/` (POST): AI grammar/style check
- `/citations/` (POST): Extract citations
- `/plagiarism_check/` (POST): Plagiarism check
- `/format_draft/` (POST): Format draft
- `/save_draft/`, `/list_drafts/`, `/get_draft/{name}`: Version control
- `/add_comment/`, `/get_comments/`: Shared comments
- `/export_draft/`, `/download_export/{filename}`: Export options

## Notes
- Do **not** commit your `.env` file or API keys to GitHub.
- Make sure CORS is enabled for frontend-backend communication.
- Error handling is basic; improve as needed for production.

---
# Fill in your actual Gemini API key and any other secrets in `.env`.
