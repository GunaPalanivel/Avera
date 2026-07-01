import logging
import os
from typing import Any

from src.config import SEMANTIC_MODEL_NAME
from src.models import CandidateModel
from src.scorers.base import BaseScorer

logger = logging.getLogger(__name__)

# Configurable for host stability; smaller batches avoid CPU/BLAS crashes on some platforms
_BATCH_SIZE = int(os.environ.get("AVERA_SEMANTIC_BATCH", "128"))


class SemanticScorer(BaseScorer):
    def __init__(self, weight: float, jd_text: str):
        super().__init__(weight)
        self.jd_text = jd_text.strip()
        self._model: Any = None
        self._jd_embedding: Any = None
        self._util: Any = None
        self._score_cache: dict[str, float] = {}
        self._prefill_complete = False

    def mark_prefill_complete(self) -> None:
        """After funnel prefill, candidates outside the reranked top-K contribute no semantic signal."""
        self._prefill_complete = True

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

    @staticmethod
    def build_candidate_text(candidate: CandidateModel) -> str:
        parts: list[str] = []
        if candidate.profile.headline:
            parts.append(candidate.profile.headline)
        if candidate.profile.summary:
            parts.append(candidate.profile.summary)
        for job in candidate.career_history:
            if job.description:
                parts.append(job.description)
        # Skills are the highest-signal field; include them so a thin-narrative but skilled
        # candidate is not under-represented in the embedding versus verbose job descriptions.
        skill_names = " ".join(s.name for s in candidate.skills)
        if skill_names:
            parts.append(skill_names)
        return " ".join(parts)

    def prefill_batch(self, candidates: list[tuple[str, CandidateModel]]) -> int:
        """Batch-encode semantic scores for (candidate_id, candidate) pairs. Returns encoded count."""
        if not candidates or not self._ensure_model():
            return 0

        pending_ids: list[str] = []
        pending_texts: list[str] = []
        encoded = 0

        for cid, candidate in candidates:
            if cid in self._score_cache:
                continue
            text = self.build_candidate_text(candidate)
            if not text:
                self._score_cache[cid] = 0.0
                continue
            pending_ids.append(cid)
            pending_texts.append(text)

            if len(pending_texts) >= _BATCH_SIZE:
                encoded += self._flush_batch(pending_ids, pending_texts)
                pending_ids = []
                pending_texts = []

        if pending_texts:
            encoded += self._flush_batch(pending_ids, pending_texts)

        logger.info(
            "semantic prefill complete",
            extra={"extra_fields": {"encoded": encoded, "cache_size": len(self._score_cache)}},
        )
        return encoded

    def _flush_batch(self, ids: list[str], texts: list[str]) -> int:
        if not ids:
            return 0
        try:
            embeddings = self._model.encode(
                texts,
                convert_to_tensor=True,
                batch_size=_BATCH_SIZE,
                show_progress_bar=False,
            )
            for idx, cid in enumerate(ids):
                similarity = self._util.cos_sim(self._jd_embedding, embeddings[idx]).item()
                self._score_cache[cid] = max(0.0, float(similarity)) * self.weight
            return len(ids)
        except Exception as e:
            logger.error("Batch semantic encode failed: %s", e)
            for cid in ids:
                self._score_cache.setdefault(cid, 0.0)
            return 0

    def score(self, candidate: CandidateModel) -> float:
        if not self.jd_text:
            return 0.0
        cached = self._score_cache.get(candidate.candidate_id)
        if cached is not None:
            return cached

        # Funnel invariant: never encode on-demand once batch prefill has run
        if self._prefill_complete:
            return 0.0

        if not self._ensure_model():
            return 0.0

        text = self.build_candidate_text(candidate)
        if not text:
            return 0.0

        try:
            cand_emb = self._model.encode(text, convert_to_tensor=True, show_progress_bar=False)
            similarity = self._util.cos_sim(self._jd_embedding, cand_emb).item()
            raw = max(0.0, float(similarity)) * self.weight
            self._score_cache[candidate.candidate_id] = raw
            return raw
        except Exception as e:
            logger.error("Error computing semantic score: %s", e)
            return 0.0
