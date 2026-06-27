import logging
from abc import ABC, abstractmethod

from src.models import CandidateModel

logger = logging.getLogger(__name__)


class ScoringError(Exception):
    pass


class BaseScorer(ABC):
    """
    Abstract base class for all candidate scorers.
    """

    def __init__(self, weight: float):
        self.weight = weight

    def __call__(self, candidate: CandidateModel) -> float:
        """
        Executes the scorer with timing observability.
        Returns a weighted score from 0.0 to self.weight.
        """
        # (Timing logic removed)
        try:
            raw_score = self.score(candidate)
            # Ensure score is bound between 0 and 1
            raw_score = max(0.0, min(1.0, raw_score))
            weighted_score = raw_score * self.weight
            return weighted_score
        except Exception as e:
            logger.error(
                "Scoring error",
                extra={"candidate_id": candidate.candidate_id, "scorer": self.__class__.__name__, "error": str(e)},
            )
            return 0.0
        finally:
            pass
            # Optional debug log for timing
            # logger.debug(f"{self.__class__.__name__} took {duration:.2f}ms")

    @abstractmethod
    def score(self, candidate: CandidateModel) -> float:
        """
        Implementation of the specific scoring logic.
        Must return a value between 0.0 and 1.0.
        """
        pass
