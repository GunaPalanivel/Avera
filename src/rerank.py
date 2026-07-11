"""Cross-encoder rerank stage (ADR-18).

Bi-encoder retrieval finds the shortlist pool; a cross-encoder then re-scores JD vs candidate
text for that pool and nudges the final order. The blend is additive and bounded
(final = min(1.0, base + alpha * ce), ce in [0,1]), so the output stays in IR convention
"""

from __future__ import annotations

import logging
import os
from typing import Any

from src.config import CROSS_ENCODER_MODEL_NAME, RERANK_ALPHA
from src.models import CandidateModel
from src.scorers.semantic_scorer import SemanticScorer

logger = logging.getLogger(__name__)

PoolItem = tuple[float, CandidateModel, str]
RerankItem = tuple[float, CandidateModel, str, float]


def _skip_rerank() -> bool:
    for var in ("AVERA_SKIP_SEMANTIC", "AVERA_SKIP_RERANK"):
        if os.environ.get(var, "").lower() in ("1", "true", "yes"):
            return True
    return False


class CrossEncoderReranker:
    def __init__(self, jd_text: str, alpha: float = RERANK_ALPHA):
        self.jd_text = jd_text.strip()
        self.alpha = alpha
        self._model: Any = None

    def _ensure_model(self) -> bool:
        if self._model is not None:
            return True
        if not self.jd_text or _skip_rerank():
            return False
        try:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(CROSS_ENCODER_MODEL_NAME)
            return True
        except Exception as e:
            logger.error("Failed to load cross-encoder, falling back to base order: %s", e)
            return False

    def rerank(self, pool: list[PoolItem], top_k: int) -> list[RerankItem]:
        """Rerank a base-sorted pool and return the top_k.

        Each item is (display_score, candidate, matched_skills_csv, raw_blended).
        Tie-break within the 1.0 display tier uses raw_blended (pre-clamp), then candidate_id.
        """
        if len(pool) <= 1 or not self._ensure_model():
            return [(s, c, m, s) for s, c, m in pool[:top_k]]

        pairs = [(self.jd_text, SemanticScorer.build_candidate_text(cand)) for _score, cand, _m in pool]
        try:
            raw_scores = self._model.predict(pairs, show_progress_bar=False)
        except Exception as e:
            logger.error("Cross-encoder predict failed, falling back to base order: %s", e)
            return [(s, c, m, s) for s, c, m in pool[:top_k]]

        blended: list[RerankItem] = []
        raw_min = min(float(r) for r in raw_scores)
        raw_max = max(float(r) for r in raw_scores)
        span = raw_max - raw_min or 1.0
        for (base_score, cand, matched), raw in zip(pool, raw_scores, strict=False):
            ce_norm = (float(raw) - raw_min) / span
            raw_blended = round(base_score + self.alpha * ce_norm, 4)
            display_score = min(1.0, raw_blended)
            blended.append((round(display_score, 4), cand, matched, raw_blended))

        blended.sort(key=lambda item: (-item[0], -item[3], item[1].candidate_id))
        return blended[:top_k]
