# app/embeddings.py\n# Embedding model wrapper.\n
# app/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Wrapper around SentenceTransformer embeddings.
        Default: 'all-MiniLM-L6-v2' (fast + lightweight).
        """
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str) -> np.ndarray:
        """Convert text into an embedding vector (numpy array)."""
        if not text:
            return np.zeros(self.model.get_sentence_embedding_dimension(), dtype=float)
        return self.model.encode(text, convert_to_numpy=True)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors (0–1)."""
    if a is None or b is None:
        return 0.0
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
