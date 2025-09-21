# Skill canonicalization and fuzzy matching logic goes here.\n
# app/skills.py
import json
from rapidfuzz import process, fuzz
from typing import Set

def load_skill_map(path: str) -> dict:
    """Load canonical skill mapping from JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

class SkillMatcher:
    def __init__(self, skill_map: dict, threshold: int = 80):
        """
        skill_map: {canonical: [synonym1, synonym2, ...]}
        threshold: fuzzy match threshold (0–100)
        """
        self.lookup = {}
        for canon, syns in skill_map.items():
            self.lookup[canon.lower()] = canon
            for s in syns:
                self.lookup[s.lower()] = canon

        self.candidates = list(self.lookup.keys())
        self.threshold = threshold

    def match(self, token: str) -> str:
        """Match a single token to canonical skill."""
        token = token.strip().lower()
        if not token:
            return ''
        if token in self.lookup:
            return self.lookup[token]
        best = process.extractOne(token, self.candidates, scorer=fuzz.token_sort_ratio)
        if best and best[1] >= self.threshold:
            return self.lookup[best[0]]
        return ''

    def extract_from_text(self, text: str) -> Set[str]:
        """Extract all skills from text based on the skill map."""
        if not text:
            return set()
        tokens = []
        for part in text.split("\n"):
            for token in part.split(","):
                token = token.strip().strip("•- –—")
                if token:
                    tokens.append(token)
        matched = set()
        for t in tokens:
            m = self.match(t)
            if m:
                matched.add(m)
        # catch inline skills too
        low = text.lower()
        for cand in self.candidates:
            if cand in low:
                matched.add(self.lookup[cand])
        return matched
