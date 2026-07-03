import os
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
            ref = os.environ.get("AVERA_REFERENCE_DATE", "2026-06-27")
            now = datetime.strptime(ref, "%Y-%m-%d")
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

        completeness = sigs.profile_completeness_score
        if completeness >= 90:
            modifier *= 1.05
        elif completeness < 40:
            modifier *= 0.9

        # Recent applications signal active job-seeking intent. Bounded 1-20: below 1 is passive,
        # above 20 in 30 days signals spray-and-pray, so neither extreme earns the availability boost.
        if 1 <= sigs.applications_submitted_30d <= 20:
            modifier *= 1.05

        return max(BEHAVIORAL_MODIFIER_MIN, min(BEHAVIORAL_MODIFIER_MAX, modifier))

    def join_probability(self, candidate: CandidateModel) -> float:
        """Informational hireability score in [0, 1]; does not affect rank."""
        sigs = candidate.redrob_signals

        offer = sigs.offer_acceptance_rate if sigs.offer_acceptance_rate is not None else 0.5
        interview = sigs.interview_completion_rate if sigs.interview_completion_rate is not None else 0.5

        notice = sigs.notice_period_days
        if notice <= 30:
            notice_factor = 1.0
        elif notice <= 60:
            notice_factor = 0.85
        elif notice <= 90:
            notice_factor = 0.7
        else:
            notice_factor = 0.5

        otw = 1.05 if sigs.open_to_work_flag else 0.9

        resp = sigs.recruiter_response_rate
        if resp >= 0.5:
            resp_factor = 1.0
        elif resp >= 0.2:
            resp_factor = 0.85
        else:
            resp_factor = 0.6

        rt = sigs.avg_response_time_hours
        if rt is None or rt <= 0:
            time_factor = 0.9
        elif rt <= 24:
            time_factor = 1.0
        elif rt <= 72:
            time_factor = 0.9
        else:
            time_factor = 0.75

        mode = (sigs.preferred_work_mode or "").lower()
        mode_factor = 1.05 if mode in ("remote", "hybrid") else 1.0

        relocate = 1.03 if sigs.willing_to_relocate else 1.0

        prob = offer * interview * notice_factor * otw * resp_factor * time_factor * mode_factor * relocate
        return max(0.0, min(1.0, prob))
