# Hybrid scoring functions.\n
# app/scoring.py
from typing import Dict, List, Set
from embeddings import EmbeddingModel, cosine_sim

def compute_hard_score(res_skills: Set[str], jd_must: List[str], jd_nice: List[str]) -> Dict:
    """
    Compute hard score from skill matches.
    Must-have skills get higher weight than nice-to-have.
    """
    jd_must = jd_must or []
    jd_nice = jd_nice or []

    must_total = max(1, len(jd_must))
    nice_total = max(1, len(jd_nice))

    must_matched = [s for s in jd_must if s in res_skills]
    nice_matched = [s for s in jd_nice if s in res_skills]

    must_part = (len(must_matched) / must_total) * 50  # weight 70%
    nice_part = (len(nice_matched) / nice_total) * 50  # weight 30%

    hard_score = must_part + nice_part
    return {
        "hard_score": round(hard_score, 2),
        "must_matched": must_matched,
        "must_missing": [s for s in jd_must if s not in must_matched],
        "nice_matched": nice_matched,
        "nice_missing": [s for s in jd_nice if s not in nice_matched],
    }

def compute_final_score(
    resume_text: str,
    jd_text: str,
    res_skills: Set[str],
    jd_must: List[str],
    jd_nice: List[str],
    emb_model: EmbeddingModel,
    weights: Dict = None
) -> Dict:
    """
    Combine hard score (skills) and semantic score (embeddings).
    """
    if weights is None:
        weights = {"hard": 0.6, "semantic": 0.4}

    hard = compute_hard_score(res_skills, jd_must, jd_nice)

    emb_res = emb_model.encode(resume_text)
    emb_jd = emb_model.encode(jd_text)
    semantic_sim = cosine_sim(emb_res, emb_jd)  # 0–1
    semantic_score = round(semantic_sim * 100, 2)

    final_score = round(weights["hard"] * hard["hard_score"] + weights["semantic"] * semantic_score)

    if final_score >= 80:
        verdict = "High"
    elif final_score >= 60:
        verdict = "Medium"
    else:
        verdict = "Low"

    return {
        "final_score": int(final_score),
        "verdict": verdict,
        "hard": hard,
        "semantic_score": semantic_score,
        "semantic_sim": round(semantic_sim, 4),
    }
