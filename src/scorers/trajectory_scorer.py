from src.config import PRODUCT_INDUSTRIES, SERVICES_INDUSTRIES
from src.models import CandidateModel, CareerEntryModel
from src.scorers.base import BaseScorer


def _title_level(title: str) -> int:
    t = title.lower()
    if any(k in t for k in ("principal", "staff", "distinguished")):
        return 4
    if "lead" in t:
        return 3
    if "senior" in t or "sr." in t or "sr " in t:
        return 2
    if any(k in t for k in ("junior", "intern", "trainee")):
        return 0
    return 1


def product_company_ratio(career: list[CareerEntryModel]) -> float:
    """Share of career months spent in product-industry companies."""
    total = sum(c.duration_months for c in career)
    if total <= 0:
        return 0.5
    product = sum(c.duration_months for c in career if c.industry in PRODUCT_INDUSTRIES)
    return product / total


class TrajectoryScorer(BaseScorer):
    """Rewards seniority progression and product-company experience.

    Down-weights consulting-only or research-only trajectories, which the JD flags as a poor fit.
    """

    def score(self, candidate: CandidateModel) -> float:
        career = candidate.career_history
        if not career:
            return 0.35

        ordered = sorted(career, key=lambda c: c.start_date)
        levels = [_title_level(c.title) for c in ordered]
        progression = max(levels) - min(levels)

        score = 0.5
        if progression >= 2:
            score += 0.3
        elif progression == 1:
            score += 0.2
        elif progression == 0:
            score += 0.1

        industries = [c.industry.lower() for c in career]
        all_services = bool(career) and all(c.industry in SERVICES_INDUSTRIES for c in career)
        research_only = bool(industries) and all(("research" in ind or "academ" in ind) for ind in industries)
        product_ratio = product_company_ratio(career)

        if all_services:
            score -= 0.2
        if research_only:
            score -= 0.15
        if product_ratio >= 0.7:
            score += 0.12
        elif product_ratio < 0.4:
            score -= 0.12
        elif not all_services and not research_only:
            score += 0.1

        return max(0.0, min(1.0, score))
