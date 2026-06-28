import logging
import os

from src.config import SEMANTIC_MODEL_NAME
from src.models import CandidateModel
from src.scorers.base import BaseScorer

logger = logging.getLogger(__name__)


class SemanticScorer(BaseScorer):
    def __init__(self, weight: float, jd_text: str):
        super().__init__(weight)
        self.jd_text = jd_text.strip()
        self._model = None
        self._jd_embedding = None
        self._util = None

    def _ensure_model(self) -> bool:
        if self._model is not None:
            return True
        if not self.jd_text:
            return False
        if os.environ.get("AVERA_SKIP_SEMANTIC", "").lower() in ("1", "true", "yes"):
            return False
        try:
            from sentence_transformers import SentenceTransformer, util

            self._util = util
            self._model = SentenceTransformer(SEMANTIC_MODEL_NAME)
            self._jd_embedding = self._model.encode(self.jd_text, convert_to_tensor=True, show_progress_bar=False)
            return True
        except Exception as e:
            logger.error("Failed to load sentence-transformers: %s", e)
            return False

    def score(self, candidate: CandidateModel) -> float:
        if not self.jd_text:
            return 0.0
        if not self._ensure_model():
            return 0.0

        cand_text_parts: list[str] = []
        if candidate.profile.headline:
            cand_text_parts.append(candidate.profile.headline)
        if candidate.profile.summary:
            cand_text_parts.append(candidate.profile.summary)

        for job in candidate.career_history:
            if job.description:
                cand_text_parts.append(job.description)

        if not cand_text_parts:
            return 0.0

        cand_text = " ".join(cand_text_parts)

        try:
            cand_emb = self._model.encode(cand_text, convert_to_tensor=True, show_progress_bar=False)
            similarity = self._util.cos_sim(self._jd_embedding, cand_emb).item()
            return max(0.0, float(similarity))
        except Exception as e:
            logger.error("Error computing semantic score: %s", e)
            return 0.0
