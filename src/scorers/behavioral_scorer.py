from datetime import datetime

from src.models import CandidateModel
from src.scorers.base import BaseScorer


class BehavioralScorer(BaseScorer):
    def score(self, candidate: CandidateModel) -> float:
        sigs = candidate.redrob_signals

        modifier = 1.0

        # 1. Availability / Ghosting (Strong penalty)
        resp_rate = sigs.recruiter_response_rate
        if resp_rate < 0.05:
            modifier *= 0.5  # "Not actually available"
        elif resp_rate < 0.20:
            modifier *= 0.8

        # 2. Inactivity (Penalty)
        try:
            last_active = datetime.strptime(sigs.last_active_date, "%Y-%m-%d")
            now = datetime(2026, 6, 27)
            months_inactive = (now - last_active).days / 30.0
            if months_inactive > 6:
                modifier *= 0.8
        except ValueError:
            pass

        # 3. Open to work / Notice Period (Bonus)
        if sigs.open_to_work_flag:
            modifier *= 1.05

        notice = sigs.notice_period_days
        if notice <= 30:
            modifier *= 1.10
        elif notice > 60:
            modifier *= 0.95

        # 4. Market Demand & Interview Reliability
        if sigs.saved_by_recruiters_30d > 10:
            modifier *= 1.05

        if sigs.interview_completion_rate >= 0.9:
            modifier *= 1.05
        elif sigs.interview_completion_rate < 0.5:
            modifier *= 0.7  # Flaky candidate

        # 5. Verification
        if sigs.verified_email and sigs.verified_phone and sigs.linkedin_connected:
            modifier *= 1.05

        return max(0.5, min(1.2, modifier))
