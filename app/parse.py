import pdfplumber
import docx2txt
import re
from typing import Optional

def extract_text(path: str) -> str:
    """
    Extract text from a .pdf, .docx, .doc, or .txt file.
    Returns cleaned text string.
    """
    text = ""
    path = str(path)

    if path.lower().endswith('.pdf'):
        with pdfplumber.open(path) as pdf:
            pages = [p.extract_text() or '' for p in pdf.pages]
            text = "\n".join(pages)

    elif path.lower().endswith('.docx') or path.lower().endswith('.doc'):
        text = docx2txt.process(path) or ''

    elif path.lower().endswith('.txt'):
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            text = ''
    else:
        raise ValueError(f"Unsupported file type: {path}")

    return clean_text(text)

def clean_text(text: Optional[str]) -> str:
    """
    Normalize whitespace, remove excess blank lines, trim edges.
    """
    if not text:
        return ''
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    # remove multiple blank lines
    t = re.sub(r'\n{2,}', '\n\n', t)
    return t.strip()
