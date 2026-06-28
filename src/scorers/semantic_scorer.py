import logging

from sentence_transformers import SentenceTransformer, util

from src.models import CandidateModel
from src.scorers.base import BaseScorer

logger = logging.getLogger(__name__)


class SemanticScorer(BaseScorer):
    def __init__(self, weight: float, jd_text: str):
        super().__init__(weight)
        self.jd_text = jd_text
        try:
            # Note: in a strict offline environment, this model would need to be pre-downloaded
            # into a local directory and loaded from there. We use the HuggingFace cache by default.
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            # compute jd embedding once
            self.jd_embedding = self.model.encode(self.jd_text, convert_to_tensor=True)
        except Exception as e:
            logger.error(f"Failed to load sentence-transformers: {e}")
            self.model = None

    def score(self, candidate: CandidateModel) -> float:
        if not self.model:
            return 0.0

        # Construct candidate text representation
        cand_text_parts = []
        if candidate.profile.headline:
            cand_text_parts.append(candidate.profile.headline)
        if candidate.profile.summary:
            cand_text_parts.append(candidate.profile.summary)

        # Add past experience descriptions for richer semantic match
        for exp in candidate.experience:
            if exp.description:
                cand_text_parts.append(exp.description)

        if not cand_text_parts:
            return 0.0

        cand_text = " ".join(cand_text_parts)

        try:
            cand_emb = self.model.encode(cand_text, convert_to_tensor=True)
            similarity = util.cos_sim(self.jd_embedding, cand_emb).item()
            return max(0.0, float(similarity))
        except Exception as e:
            logger.error(f"Error computing semantic score: {e}")
            return 0.0
