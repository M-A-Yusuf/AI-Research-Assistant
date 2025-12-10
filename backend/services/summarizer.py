import os
import time
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
)

# -----------------------------------------------------------
# 🔹 Gemini API Caller
# -----------------------------------------------------------

def call_gemini_api(prompt: str, retries: int = 3, timeout: int = 60) -> str:
    """Call Gemini API with retries and timeout."""
    for attempt in range(retries):
        try:
            response = requests.post(
                GEMINI_API_URL,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=timeout,
            )

            if response.status_code == 200:
                data = response.json()
                return (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "[No text returned]")
                )

            return f"[Gemini API Error {response.status_code}] {response.text}"

        except requests.exceptions.ReadTimeout:
            if attempt < retries - 1:
                time.sleep(1.5)
                continue
            return "[Gemini Timeout Error] Request timed out."

        except Exception as e:
            return f"[Gemini API Exception] {str(e)}"


# -----------------------------------------------------------
# 🔹 Normal Summaries
# -----------------------------------------------------------

def chunk_text(text, max_words=500):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i : i + max_words])


def summarize_text(text: str, max_length: int = 300, min_length: int = 100) -> str:
    prompt = (
        f"Summarize the following academic text in {min_length}-{max_length} words:\n{text}"
    )
    return call_gemini_api(prompt)


def summarize_large_text(full_text: str) -> str:
    partials = []
    for chunk in chunk_text(full_text):
        partials.append(summarize_text(chunk, 150, 50))
    combined = " ".join(partials)
    return summarize_text(combined, 300, 100)


# -----------------------------------------------------------
# 🔹 Outline Generator
# -----------------------------------------------------------

def generate_outline(text: str, max_sections: int = 7) -> list:
    prompt = f"""
Create a structured outline (up to {max_sections} sections)
for a research paper based on this text.

Format EXACTLY like this:
1) Heading - short note
2) Heading - short note
...

Text:
{text[:3000]}
"""
    resp = call_gemini_api(prompt)

    outline = []
    for line in resp.splitlines():
        line = line.strip()
        if not line or "-" not in line:
            continue

        heading_part, note = line.split("-", 1)
        note = note.strip()

        # Clean heading part
        heading_raw = heading_part.strip()
        heading = heading_raw
        for sep in [")", ".", "]"]:
            if sep in heading_raw:
                heading = heading_raw.split(sep, 1)[1].strip()
                break

        outline.append((heading, note))
        if len(outline) >= max_sections:
            break

    if not outline:
        outline = [
            ("Introduction", "overview"),
            ("Methodology", "methods"),
            ("Results", "findings"),
            ("Discussion", "analysis"),
            ("Conclusion", "closing points"),
        ]

    return outline


# -----------------------------------------------------------
# 🔹 Section Expansion
# -----------------------------------------------------------

def expand_section(section_heading: str, note: str, text: str, approx_words: int = 350):
    prompt = f"""
Write an academic section titled "{section_heading}".
Short note: {note}

Length: ~{approx_words} words.
Use ONLY the following research text. Do NOT invent numerical results.

Research text:
{text[:5000]}
"""
    return call_gemini_api(prompt)


# -----------------------------------------------------------
# 🔥 FAST FULL RESEARCH PAPER GENERATOR (Batch Mode)
# -----------------------------------------------------------

def generate_full_paper_from_text(
    text: str,
    title: str = None,
    max_sections: int = 6,
    approx_words_per_section: int = 350,
    batch_mode: bool = True,
):
    """Fast full research paper generator using batch-mode section expansion."""

    # ---------- 1) Title ----------
    if not title:
        title_prompt = f"Generate a concise academic title (8-12 words) for this text:\n{text[:2000]}"
        title = call_gemini_api(title_prompt).split("\n")[0].strip()

    # ---------- 2) Abstract ----------
    abstract_prompt = f"""
Write an academic abstract (150–220 words) for the paper titled "{title}".
Use only information from the text. No invented numbers.

Text:
{text[:4000]}
"""
    abstract = call_gemini_api(abstract_prompt)

    # ---------- 3) Outline ----------
    outline = generate_outline(text, max_sections)

    # ---------- 4) Batch Section Expansion (FASTEST) ----------
    if batch_mode:
        outline_text = "\n".join(
            [f"{i+1}) {h} - {n}" for i, (h, n) in enumerate(outline)]
        )

        batch_prompt = f"""
You are an academic writing assistant.
Expand ALL sections below into detailed academic sections.

OUTPUT FORMAT (exact!):
---SECTION X START---
Title: <title>
Content: <full text>
---SECTION X END---

Outline:
{outline_text}

Research text:
{text[:10000]}

Write sections 1 to {len(outline)}, IN ORDER.
"""
        resp = call_gemini_api(batch_prompt, timeout=120)

        sections = []
        for i, (heading, _) in enumerate(outline, start=1):
            start = f"---SECTION {i} START---"
            end = f"---SECTION {i} END---"

            if start in resp and end in resp:
                content = resp.split(start, 1)[1].split(end, 1)[0].strip()

                # Remove "Title:" and keep content
                if "Content:" in content:
                    content = content.split("Content:", 1)[1].strip()

                sections.append((heading, content))
            else:
                # fallback
                sections.append(
                    (heading, expand_section(heading, "", text, approx_words_per_section))
                )
    else:
        # ------------ PAINFULLY SLOW MODE (Not recommended) -------------
        sections = []
        for heading, note in outline:
            body = expand_section(heading, note, text, approx_words_per_section)
            sections.append((heading, body))

    # ---------- 5) References ----------
    refs_prompt = f"""
Extract a references list (5–12 items) from the text.
If references are unclear, output "References available upon request".

Text:
{text[:4000]}
"""
    references = call_gemini_api(refs_prompt)

    # ---------- 6) Assemble the final paper ----------
    final = []

    final.append(title + "\n")
    final.append("Abstract\n" + abstract + "\n")

    for heading, body in sections:
        final.append(f"{heading}\n{body}\n")

    final.append("References\n" + references + "\n")

    return "\n\n".join(final)


# -----------------------------------------------------------
# 🔹 PDF Wrapper
# -----------------------------------------------------------

def generate_full_paper_from_pdf(pdf_path: str, title: str = None, **kwargs):
    """Extract text from PDF then generate paper."""
    from backend.services.pdf_utils import extract_text_from_pdf

    raw = extract_text_from_pdf(pdf_path)
    cleaned = " ".join(raw.encode("utf-8", "ignore").decode("utf-8").split())

    return generate_full_paper_from_text(cleaned, title=title, **kwargs)
