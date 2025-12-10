import re

def extract_citations(text: str):
    # Simple regex for APA/MLA/IEEE-like citations (demo only)
    apa = re.findall(r'\([A-Za-z]+, \d{4}\)', text)
    ieee = re.findall(r'\[\d+\]', text)
    return {"apa": apa, "ieee": ieee}
