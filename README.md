# 📑 Resume Relevance Check System

An AI-powered system that evaluates resumes against job descriptions (JDs) and generates:
- Relevance scores (0–100)
- Verdicts (High / Medium / Low)
- Matched vs missing skills
- Candidate Fit Reports (PDF)
- Personalized recommendations
- Multi-JD comparison matrix
- Visual insights (charts + word cloud)

---

## 🚀 Features
✅ Automated resume parsing (PDF/DOCX/TXT)  
✅ JD parsing (must-have / nice-to-have skills)  
✅ Hard + semantic matching (Sentence-Transformers)  
✅ Recruiter dashboard (Streamlit)  
✅ Candidate Fit Reports (downloadable PDF)  
✅ Personalized skill recommendations  
✅ Multi-JD matching matrix  
✅ Export results as CSV  

---

## 🛠 Tech Stack
- **Python** (main logic)
- **Streamlit** (dashboard UI)
- **fpdf** (PDF reports)
- **RapidFuzz** (fuzzy matching)
- **Sentence-Transformers** (semantic similarity)
- **SQLite** (storage)