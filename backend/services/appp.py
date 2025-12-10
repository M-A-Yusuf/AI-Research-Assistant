import os
import sys

# Go from .../backend/services/appp.py -> .../ (project root)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)       # .../backend
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)      # .../

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)




import streamlit as st
import tempfile
import datetime

from backend.services.pdf_utils import extract_text_from_pdf
from backend.services.citations import extract_citations
from backend.services.summarizer import (
    summarize_large_text,
    summarize_text,
    generate_full_paper_from_text
)

from backend.services.pdf_export import generate_pdf


# ---------------------------------------------------------
# Session State: HISTORY STORAGE
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = {
        "summaries": [],
        "citations": [],
        "papers": []
    }

if "view_history" not in st.session_state:
    st.session_state.view_history = None


# ---- Streamlit Page Config ----
st.set_page_config(page_title="AI Research Paper Assistant", page_icon="🧠", layout="wide")

# ---- 🎨 Premium Neo-AI Styling ----
st.markdown("""
<style>
body, .stApp {
    background: radial-gradient(circle at 50% 20%, #eef2ff, #ffffff 70%);
    font-family: 'Inter', sans-serif;
    color: #1e1e1e;
}

.header h1 {
    font-size: 2.9rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.header p {
    font-size: 1.05rem;
    color: #4b5563;
}

.main-card {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(18px);
    border-radius: 16px;
    padding: 2rem 2.4rem;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
}

.stButton>button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
}

/* FIXED TEXTAREA — TEXT FULLY VISIBLE AGAIN */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid #d1d5db !important;
    background-color: #ffffff !important;    /* strong contrast background */
    color: #1f2937 !important;                /* dark, readable text */
    font-size: 0.98rem !important;
    line-height: 1.6 !important;
    padding: 14px !important;
    resize: vertical !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.04);
    caret-color: #111827 !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
}

.stTextArea textarea::selection {
    background-color: #c7d2fe !important;
    color: #0b1220 !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #1f2937);
    color: #fff;
}
</style>
""", unsafe_allow_html=True)


# ---- Header ----
st.markdown("""
<div class="header" style="text-align:center;">
    <h1>🧠 AI Research Paper Assistant</h1>
    <p>Summarize, analyze & generate full research papers instantly.</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# SIDEBAR — HISTORY SYSTEM
# ---------------------------------------------------------
st.sidebar.header("📌 Input Mode")
mode = st.sidebar.radio("Choose:", ["📄 Upload PDF", "📝 Paste Text"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📜 History")

# Summaries
if st.session_state.history["summaries"]:
    st.sidebar.markdown("**📝 Summaries**")
    for idx, item in enumerate(st.session_state.history["summaries"]):
        if st.sidebar.button(f"Summary {idx+1} ({item['timestamp']})"):
            st.session_state.view_history = item["content"]

# Citations
if st.session_state.history["citations"]:
    st.sidebar.markdown("**🔗 Citations**")
    for idx, item in enumerate(st.session_state.history["citations"]):
        if st.sidebar.button(f"Citations {idx+1} ({item['timestamp']})"):
            st.session_state.view_history = item["content"]

# Full Papers
if st.session_state.history["papers"]:
    st.sidebar.markdown("**📄 Full Papers**")
    for idx, item in enumerate(st.session_state.history["papers"]):
        if st.sidebar.button(f"Paper {idx+1} ({item['timestamp']})"):
            st.session_state.view_history = item["content"]

# Clear history
if st.sidebar.button("🗑️ Clear All History"):
    st.session_state.history = {"summaries": [], "citations": [], "papers": []}
    st.session_state.view_history = None
    st.sidebar.success("History cleared!")


# ---------------------------------------------------------
# MAIN INPUT AREA
# ---------------------------------------------------------
input_text = ""

with st.container():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)

    if mode == "📄 Upload PDF":
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
        if pdf_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_file.read())
                pdf_path = tmp.name

            with st.spinner("⏳ Extracting text…"):
                raw_text = extract_text_from_pdf(pdf_path)

            os.remove(pdf_path)

            input_text = " ".join(raw_text.split())

            if not input_text.strip():
                st.warning("⚠️ No readable text found in PDF.")
            else:
                st.success("✅ PDF extracted!")
                st.text_area(
                    "Extracted Text Preview:",
                    input_text[:1200] + ("..." if len(input_text) > 1200 else ""),
                    height=220,
                )

    else:
        input_text = st.text_area("Paste your research text here:", height=260)

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# BUTTONS
# ---------------------------------------------------------
colA, colB = st.columns([1, 1])
analyze_btn = colA.button("🔍 Analyze")
fullpaper_btn = colB.button("📝 Generate Full Research Paper")


# ---------------------------------------------------------
# ANALYZE LOGIC
# ---------------------------------------------------------
if analyze_btn:
    if not input_text.strip():
        st.warning("Please provide input text first.")
    else:
        with st.spinner("🤖 Analyzing…"):
            summary = summarize_large_text(input_text) if len(input_text.split()) > 600 else summarize_text(input_text)
            citations = extract_citations(input_text)

        # Save to history
        st.session_state.history["summaries"].append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": summary
        })

        st.session_state.history["citations"].append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": str(citations)
        })

        # Display
        tabs = st.tabs(["📘 Summary", "🔗 Citations"])
        tabs[0].write(summary)
        tabs[1].json(citations)

        st.download_button("📥 Download Summary", summary, "summary.txt")


# ---------------------------------------------------------
# FULL PAPER GENERATION
# ---------------------------------------------------------
if fullpaper_btn:
    if not input_text.strip():
        st.warning("Please provide input text first.")
    else:
        with st.spinner("🧠 Generating full research paper…"):
            full_paper = generate_full_paper_from_text(
                text=input_text,
                max_sections=6,
                approx_words_per_section=300,
                batch_mode=True
            )

        # Save to history
        st.session_state.history["papers"].append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": full_paper
        })

        st.success("✅ Research paper ready!")

        with st.expander("📄 View Full Paper", expanded=True):
            st.text_area("Full Paper:", full_paper, height=700)

        # Extract pieces
        try:
            title = full_paper.split("\n")[0].strip()
            abstract = full_paper.split("Abstract", 1)[1].split("\n", 2)[2]
        except:
            title = "Generated Research Paper"
            abstract = "Abstract not parsed."

        sections = []
        for block in full_paper.split("\n\n"):
            if block.strip() and not block.startswith(title) and "References" not in block:
                if "\n" in block:
                    heading = block.split("\n")[0].strip()
                    content = "\n".join(block.split("\n")[1:])
                    sections.append((heading, content))

        references = (
            full_paper.split("References", 1)[1].strip()
            if "References" in full_paper
            else "References available upon request."
        )

        pdf_path = generate_pdf(title, abstract, sections, references)

        with open(pdf_path, "rb") as f:
            st.download_button(
                "📥 Download as PDF",
                f,
                "Research_Paper.pdf",
                "application/pdf"
            )

        st.download_button(
            "⬇️ Download as .txt",
            full_paper,
            "research_paper.txt",
            "text/plain"
        )


# ---------------------------------------------------------
# SHOW SELECTED HISTORY ITEM
# ---------------------------------------------------------
if st.session_state.view_history:
    st.markdown("## 📄 Selected History Item")
    st.text_area("History Item:", st.session_state.view_history, height=400)


# ---- Footer ----
st.markdown("<div class='footer'>Made with ❤️ for researchers.</div>", unsafe_allow_html=True)
