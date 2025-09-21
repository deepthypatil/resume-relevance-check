# Streamlit UI code.\n
import os
import re
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from utils import generate_report

from parse import extract_text
from sections import split_sections
from skills import load_skill_map, SkillMatcher
from embeddings import EmbeddingModel
from scoring import compute_final_score
from storage import init_db, save_result, get_all_results
from utils import highlight_skills


st.set_page_config(page_title="Resume Relevance System", layout="wide")


@st.cache_resource
def load_models():
    skill_map = load_skill_map("data/skill_map.json")
    matcher = SkillMatcher(skill_map)
    emb = EmbeddingModel()
    return matcher, emb


def parse_jd_text(jd_text: str):
    """Extract must-have and nice-to-have skills from JD text more reliably."""
    if not jd_text:
        return [], []

    must, nice = [], []
    lines = [l.strip() for l in jd_text.splitlines() if l.strip()]

    capture = None
    for ln in lines:
        low = ln.lower()

        # Detect section headers
        if "must-have" in low or "must have" in low or "required" in low:
            capture = "must"
            continue
        elif "nice-to-have" in low or "nice to have" in low:
            capture = "nice"
            continue
        elif "qualification" in low or "responsibility" in low or "role" in low:
            # Stop capturing once we reach a new unrelated section
            capture = None
            continue

        # Collect skills under the right section
        if capture:
            tokens = [t.strip().lower() for t in re.split(r",|;|-", ln) if t.strip()]
            if capture == "must":
                must.extend(tokens)
            elif capture == "nice":
                nice.extend(tokens)

    return list(set(must)), list(set(nice))


def main():
    st.title("📑 Resume Relevance Check System")
    init_db()
    matcher, emb = load_models()

    st.sidebar.header("Upload Files")
    jd_file = st.sidebar.file_uploader("Upload JD (pdf/docx/txt)", type=["pdf", "docx", "txt"])
    jd_text_area = st.sidebar.text_area("Or paste JD text", height=200)
    resumes = st.sidebar.file_uploader("Upload resumes", type=["pdf", "docx", "txt"], accept_multiple_files=True)

    weights_hard = st.sidebar.slider("Hard score weight", 0.0, 1.0, 0.5)
    weights_sem = 1.0 - weights_hard

    jd_text = ""
    if jd_file and not jd_text_area:
        tmp_path = os.path.join("data", jd_file.name)
        with open(tmp_path, "wb") as f:
            f.write(jd_file.read())
        jd_text = extract_text(tmp_path)
    else:
        jd_text = jd_text_area

    if st.sidebar.button("Process"):
        if not jd_text or not resumes:
            st.sidebar.error("Please upload both JD and resumes")
            return

        results = []
        progress = st.progress(0)
        for idx, r in enumerate(resumes):
            fname = r.name
            tmp_path = os.path.join("data", fname)
            with open(tmp_path, "wb") as f:
                f.write(r.getbuffer())

            text = extract_text(tmp_path)
            sections = split_sections(text)
            res_skills = matcher.extract_from_text(sections.get("skills", "") or text)

            jd_must, jd_nice = parse_jd_text(jd_text)
            jd_must = [matcher.match(x) or x for x in jd_must]
            jd_nice = [matcher.match(x) or x for x in jd_nice]

            # Debug output to verify parsing
            #st.write("DEBUG → JD Must-have Parsed:", jd_must)
            #st.write("DEBUG → JD Nice-to-have Parsed:", jd_nice)
            #st.write("DEBUG → Resume Skills Extracted:", list(res_skills))

            score_obj = compute_final_score(
                text, jd_text, res_skills, jd_must, jd_nice, emb,
                weights={"hard": weights_hard, "semantic": weights_sem}
            )

            output = {
                "filename": fname,
                "final_score": score_obj["final_score"],
                "verdict": score_obj["verdict"],
                "must_matched": score_obj["hard"]["must_matched"],
                "must_missing": score_obj["hard"]["must_missing"],
                "nice_matched": score_obj["hard"]["nice_matched"],
                "nice_missing": score_obj["hard"]["nice_missing"],
                "semantic_score": score_obj["semantic_score"]
            }

            save_result({**output, "parsed_sections": sections})
            results.append(output)
            progress.progress((idx + 1) / len(resumes))

        df = pd.DataFrame(results).sort_values("final_score", ascending=False)
        st.success("Processing complete!")
        st.dataframe(df)

        if not df.empty:
            # Show top candidates
            st.markdown("### 🏆 Top Candidates")
            st.dataframe(df.head(5))

            # Show insights
            st.markdown("### 📊 Insights")

            # Bar chart
            verdict_counts = df["verdict"].value_counts()
            fig, ax = plt.subplots()
            verdict_counts.plot(kind="bar", ax=ax, color=["#4CAF50", "#FFC107", "#F44336"])
            ax.set_title("Resume Verdict Distribution")
            ax.set_xlabel("Verdict")
            ax.set_ylabel("Number of Resumes")
            st.pyplot(fig)

            # Word cloud
            all_skills = []
            for r in get_all_results():
                skills_text = r.parsed_json.get("parsed_sections", {}).get("skills", "")
                if skills_text:
                    all_skills.extend(skills_text.split(","))
            all_skills_text = " ".join(all_skills)

            if all_skills_text.strip():
                wc = WordCloud(width=800, height=400, background_color="white").generate(all_skills_text)
                fig_wc, ax_wc = plt.subplots()
                ax_wc.imshow(wc, interpolation="bilinear")
                ax_wc.axis("off")
                st.pyplot(fig_wc)

            # Candidate detail view
            st.markdown("---")
            sel = st.selectbox("View candidate details", df["filename"].tolist())
            if sel:
                row = df[df["filename"] == sel].iloc[0]
                st.subheader(f"{sel} — Score: {row['final_score']} ({row['verdict']})")

                for r in get_all_results():
                    if r.filename == sel:
                        parsed = r.parsed_json.get("parsed_sections", {})
                        matched = row["must_matched"] + row["nice_matched"]
                        missing = row["must_missing"] + row["nice_missing"]

                        st.markdown("**Extracted Skills:**")
                        st.write(parsed.get("skills", "") or "No explicit skills section found.")

                        st.markdown("**Highlighted Resume Sections:**")
                        raw_text = "\n".join([
                            parsed.get("summary", ""),
                            parsed.get("experience", ""),
                            parsed.get("projects", "")
                        ])
                        html = highlight_skills(raw_text, matched, missing)
                        st.markdown(html, unsafe_allow_html=True)
            st.markdown("### Recommendations")
            recommendations = []
            for skill in row["must_missing"] + row["nice_missing"]:
                recommendations.append(f"- Learn **{skill}** → [Free course](https://www.coursera.org/search?query={skill})")

            if recommendations:
                st.markdown("\n".join(recommendations))
            else:
                st.success("This candidate already matches very well. 🎉")

            report_path = generate_report(sel, row.to_dict(), jd_text)
            with open(report_path, "rb") as f:
                st.download_button("📥 Download Candidate Report", f, file_name=f"{sel}_report.pdf")
        # CSV download
        csv = df.to_csv(index=False)
        st.download_button("Export CSV", csv, file_name="results.csv", mime="text/csv")


if __name__ == "__main__":
    main()
