# Section detection logic goes here.\n
import re
from typing import Dict

HEADINGS = [
    "skills", "technical skills", "experience", "work experience",
    "projects", "education", "certifications", "summary", "objective"
]

def split_sections(text: str) -> Dict[str, str]:
    """
    Split resume text into sections based on common headings.
    Returns a dict: {section_name: section_text}.
    """
    lines = [l.strip() for l in text.splitlines()]
    sections = {h: "" for h in HEADINGS}
    current = "other"
    buffer = []

    for ln in lines:
        stripped = ln.strip().rstrip(":")
        low = stripped.lower()

        if low in HEADINGS:
            # save previous section
            if current in sections:
                sections[current] = "\n".join(buffer).strip()
            buffer = []
            current = low
            continue

        # detect ALL CAPS headings (like "EXPERIENCE")
        if re.match(r"^[A-Z\s]{4,}$", stripped) and stripped.lower() in [h.upper() for h in HEADINGS]:
            if current in sections:
                sections[current] = "\n".join(buffer).strip()
            buffer = []
            current = stripped.lower()
            continue

        buffer.append(ln)

    # flush last
    if current in sections:
        sections[current] = "\n".join(buffer).strip()
    else:
        sections["summary"] = "\n".join(buffer).strip()

    return sections

def extract_experience_years(text: str) -> int:
    """
    Estimate total years of experience from the experience section.
    Looks for years like 2018-2021.
    """
    exp = text or ""
    years = re.findall(r"(20\d{2})", exp)
    if len(years) >= 2:
        try:
            years = [int(y) for y in years]
            return max(years) - min(years)
        except Exception:
            return 0
    return 0
