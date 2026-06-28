import logging
import time
from abc import ABC, abstractmethod

from src.models import CandidateModel

logger = logging.getLogger(__name__)


class ScoringError(Exception):
    pass


class BaseScorer(ABC):
    """Abstract base class for all candidate scorers."""

    def __init__(self, weight: float):
        self.weight = weight

    def __call__(self, candidate: CandidateModel) -> float:
        start = time.perf_counter()
        try:
            raw_score = self.score(candidate)
            raw_score = max(0.0, min(1.0, raw_score))
            weighted_score = raw_score * self.weight
            return weighted_score
        except Exception as e:
            logger.error(
                "Scoring error",
                extra={
                    "candidate_id": candidate.candidate_id,
                    "scorer": self.__class__.__name__,
                    "error": str(e),
                },
            )
            return 0.0
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.debug(
                "%s scored candidate in %.2fms",
                self.__class__.__name__,
                duration_ms,
                extra={
                    "candidate_id": candidate.candidate_id,
                    "scorer": self.__class__.__name__,
                    "duration_ms": round(duration_ms, 2),
                },
            )

    @abstractmethod
    def score(self, candidate: CandidateModel) -> float:
        """Return a value between 0.0 and 1.0."""
        pass
