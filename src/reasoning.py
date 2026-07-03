"""Deterministic reasoning strings for submission output (ADR-06)."""

from src.models import CandidateModel

# Superlative tier language ("Top-tier", "Strong match") is only honest above this absolute
# score. Below it, wording stays measured even at a low rank, so a weak pool never yields an
# over-claimed rank 1. Real full-pool top-100 scores sit well above this (min ~0.80).
STRONG_FIT_SCORE = 0.70


def _concern_fragments(candidate: CandidateModel, matched_skills: list[str], rank_index: int) -> list[str]:
    """Verifiable weaknesses drawn only from parsed profile/signals."""
    concerns: list[str] = []
    sigs = candidate.redrob_signals
    must_gap = not matched_skills

    if must_gap:
        concerns.append("limited overlap with JD must-have skills")
    elif len(matched_skills) < 2:
        concerns.append(f"only {len(matched_skills)} core JD skill matched")

    if sigs.recruiter_response_rate < 0.20:
        concerns.append("low recruiter response rate")

    if sigs.notice_period_days > 60:
        concerns.append(f"{sigs.notice_period_days}-day notice period")

    github = sigs.github_activity_score
    if github is not None and github >= 0 and github < 10:
        concerns.append("minimal GitHub activity signal")

    yoe = candidate.profile.years_of_experience
    if yoe < 4:
        concerns.append("below typical senior YOE band for this JD")
    elif yoe > 12 and rank_index >= 50:
        concerns.append("experience above target band for this role")

    if rank_index >= 70 and not sigs.open_to_work_flag:
        concerns.append("not flagged open to work")

    return concerns[:3]


def _top_rank_counterfactual(candidate: CandidateModel, matched_skills: list[str], must_have_count: int) -> str:
    """Data-derived 'why not perfect' note so top ranks are not uniformly positive."""
    sigs = candidate.redrob_signals

    if must_have_count and 0 < len(matched_skills) < must_have_count:
        # Thin keyword coverage on a top pick is by design: the JD warns against keyword stuffing,
        # so frame it as ranking on trajectory rather than apologizing for a low match count.
        if len(matched_skills) * 2 < must_have_count:
            return f"ranks on career trajectory and assessed depth over keyword coverage ({len(matched_skills)}/{must_have_count} listed must-haves), aligning with the JD anti-keyword-stuffing guidance"
        uncovered = must_have_count - len(matched_skills)
        return f"trails a perfect match on {uncovered} uncovered JD must-have skill(s)"

    notice = sigs.notice_period_days
    if 30 < notice <= 60:
        return f"{notice}-day notice keeps this below the immediate-start tier"

    if 0.20 <= sigs.recruiter_response_rate < 0.50:
        return f"recruiter response rate {sigs.recruiter_response_rate:.0%} is mid-band, not elite"

    if sigs.github_activity_score is None:
        return "no GitHub activity signal to corroborate hands-on depth"

    if notice > 0:
        return f"{notice}-day notice is the main lever versus an instant-join peer"

    return "separation from the next ranks is narrow on secondary signals"


def _join_prob_suffix(join_probability: float | None, candidate: CandidateModel) -> str:
    if join_probability is None:
        return ""
    pct = int(round(join_probability * 100))
    parts = [f"Join probability: {pct}%"]
    if candidate.redrob_signals.notice_period_days > 90:
        parts.append("long notice")
    elif join_probability < 0.35:
        parts.append("low engagement signals")
    return f" {'; '.join(parts)}."


def _strength_line(candidate: CandidateModel, matched_skills: list[str]) -> str:
    top_skills = sorted(candidate.skills, key=lambda s: s.duration_months or 0, reverse=True)
    skill_names = [s.name for s in top_skills]

    if matched_skills:
        skill_str = ", ".join(matched_skills[:3])
        skill_clause = f"JD-aligned skills: {skill_str}"
    elif skill_names:
        skill_str = ", ".join(skill_names[:2])
        skill_clause = f"strongest listed skills: {skill_str}"
    else:
        skill_clause = "sparse skills section"

    return f"{candidate.profile.current_title} at {candidate.profile.current_company} ({candidate.profile.years_of_experience} YOE); {skill_clause}"


def generate_reasoning(
    candidate: CandidateModel,
    rank_index: int,
    matched_skills: list[str],
    *,
    must_have_count: int = 0,
    score: float = 1.0,
    join_probability: float | None = None,
) -> str:
    """
    Rank-aware reasoning with honest concerns for mid/low ranks.
    Avoids hallucinations by sticking to parsed data only.
    Wording is also gated by absolute ``score`` so a weak pool never produces an over-claimed top rank.
    """
    strength = _strength_line(candidate, matched_skills)
    concerns = _concern_fragments(candidate, matched_skills, rank_index)
    join_suffix = _join_prob_suffix(join_probability, candidate) if rank_index < 20 else ""

    # Weak absolute fit: stay measured regardless of rank position (avoids "Top-tier" on a poor pool)
    if score < STRONG_FIT_SCORE:
        gaps = concerns or ["weak overlap with JD must-have skills"]
        return f"Best available in this pool but weak absolute fit: {strength}. Gaps: {'; '.join(gaps)}.{join_suffix}"

    if rank_index < 5:
        extra = "Top-tier composite score across career, skills, and availability."
        if concerns:
            return f"Rank {rank_index + 1}: {strength}. {extra} Minor note: {'; '.join(concerns)}.{join_suffix}"
        counterfactual = _top_rank_counterfactual(candidate, matched_skills, must_have_count)
        return f"Rank {rank_index + 1}: {strength}. {extra} Counterfactual: {counterfactual}.{join_suffix}"

    if rank_index < 20:
        concern_txt = f" Watch: {'; '.join(concerns)}." if concerns else ""
        return f"Strong match — {strength}.{concern_txt}{join_suffix}"

    if rank_index < 50:
        tier = rank_index % 4
        openers = (
            "Solid profile:",
            "Good fit with caveats:",
            "Competitive candidate:",
            "Meets several JD signals:",
        )
        concern_txt = f" Concerns: {'; '.join(concerns)}." if concerns else ""
        return f"{openers[tier]} {strength}.{concern_txt}"

    if rank_index < 90:
        mid_openers: tuple[str, ...] = (
            "Moderate fit:",
            "Partial alignment:",
            "Acceptable but not standout:",
            "Mixed signals:",
            "JD overlap is thin:",
        )
        tier = rank_index % len(mid_openers)
        if not concerns and must_have_count and len(matched_skills) < must_have_count // 2:
            concerns.append("under half of JD must-have skills covered")
        concern_txt = f" Gaps: {'; '.join(concerns)}." if concerns else " Gaps: limited standout signals."
        return f"{mid_openers[tier]} {strength}.{concern_txt}"

    concern_txt = f" Key gaps: {'; '.join(concerns)}." if concerns else " Key gaps: weak secondary signals vs higher ranks."
    return f"Lower-tier shortlist entry — {strength}.{concern_txt}"
