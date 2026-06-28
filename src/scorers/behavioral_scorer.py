from datetime import datetime

from src.config import BEHAVIORAL_MODIFIER_MAX, BEHAVIORAL_MODIFIER_MIN
from src.models import CandidateModel
from src.scorers.base import BaseScorer


class BehavioralScorer(BaseScorer):
    def score(self, candidate: CandidateModel) -> float:
        sigs = candidate.redrob_signals

        modifier = 1.0

        resp_rate = sigs.recruiter_response_rate
        if resp_rate < 0.05:
            modifier *= 0.5
        elif resp_rate < 0.20:
            modifier *= 0.8

        try:
            last_active = datetime.strptime(sigs.last_active_date, "%Y-%m-%d")
            now = datetime(2026, 6, 27)
            months_inactive = (now - last_active).days / 30.0
            if months_inactive > 6:
                modifier *= 0.8
        except ValueError:
            pass

        if sigs.open_to_work_flag:
            modifier *= 1.05

        notice = sigs.notice_period_days
        if notice <= 30:
            modifier *= 1.10
        elif notice > 60:
            modifier *= 0.95

        if sigs.saved_by_recruiters_30d > 10:
            modifier *= 1.05

        if sigs.search_appearance_30d > 50:
            modifier *= 1.05

        if sigs.interview_completion_rate >= 0.9:
            modifier *= 1.05
        elif sigs.interview_completion_rate < 0.5:
            modifier *= 0.7

        if sigs.offer_acceptance_rate is not None:
            if sigs.offer_acceptance_rate < 0.3:
                modifier *= 0.8
            elif sigs.offer_acceptance_rate > 0.8:
                modifier *= 1.05

        if sigs.github_activity_score is not None and sigs.github_activity_score >= 80:
            modifier *= 1.10

        if sigs.verified_email and sigs.verified_phone and sigs.linkedin_connected:
            modifier *= 1.05

        return max(BEHAVIORAL_MODIFIER_MIN, min(BEHAVIORAL_MODIFIER_MAX, modifier))
