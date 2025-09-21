# app/utils.py\n# Helper functions for highlighting, etc.\n
# app/utils.py
import re
from fpdf import FPDF
def highlight_skills(text: str, matched: list, missing: list) -> str:
    """Return HTML highlighting matched (green) and missing (red) skills."""
    if not text:
        return ""
    html = text

    # highlight matched in green
    matched_sorted = sorted(set(matched), key=lambda x: -len(x))
    for m in matched_sorted:
        if m:
            html = re.sub(f"(?i)\\b{re.escape(m)}\\b",
                          f"<mark style='background:#b7f5c6'>{m}</mark>", html)

    # highlight missing in red
    missing_sorted = sorted(set(missing), key=lambda x: -len(x))
    for m in missing_sorted:
        if m:
            html = re.sub(f"(?i)\\b{re.escape(m)}\\b",
                          f"<span style='background:#ffd6d6;border-bottom:1px dashed #ff0000'>{m}</span>", html)
    return html


def generate_report(candidate_name, result, jd_text, path="candidate_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"Candidate Fit Report: {candidate_name}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Final Score: {result['final_score']} ({result['verdict']})")

    pdf.ln(5)
    pdf.multi_cell(0, 10, "Must-have Skills")
    pdf.multi_cell(0, 10, f"Matched: {', '.join(result['must_matched']) or 'None'}")
    pdf.multi_cell(0, 10, f"Missing: {', '.join(result['must_missing']) or 'None'}")

    pdf.ln(5)
    pdf.multi_cell(0, 10, "Nice-to-have Skills")
    pdf.multi_cell(0, 10, f"Matched: {', '.join(result['nice_matched']) or 'None'}")
    pdf.multi_cell(0, 10, f"Missing: {', '.join(result['nice_missing']) or 'None'}")

    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Semantic Similarity: {result['semantic_score']:.2f}")

    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Job Description (excerpt):\n{jd_text[:400]}...")

    pdf.output(path)
    return path
