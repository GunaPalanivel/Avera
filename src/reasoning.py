from src.models import CandidateModel


def generate_reasoning(candidate: CandidateModel, rank_index: int, matched_skills: list[str]) -> str:
    """
    Generate dynamic reasoning for a candidate based on ADR-06 templates.
    Avoids hallucinations by sticking to parsed data.
    """
    top_skills = sorted(candidate.skills, key=lambda s: s.duration_months, reverse=True)
    skill_names = [s.name for s in top_skills]

    # Prioritize matched JD skills if any
    if matched_skills:
        skill_str = " and ".join(matched_skills[:2])
    elif skill_names:
        skill_str = " and ".join(skill_names[:2])
    else:
        skill_str = "AI technologies"

    base_reasoning = f"Strong fit: {candidate.profile.current_title} at {candidate.profile.current_company} with {candidate.profile.years_of_experience} YOE. Demonstrates deep expertise in {skill_str}."

    # ADR-06 Tone Variation based on rank
    if rank_index < 5:
        return f"Exceptional Top 5 Match: {base_reasoning} Highly recommended for immediate interview."
    elif rank_index >= 90:
        return f"Borderline Match: {base_reasoning} Meets minimum bar but lacks standout secondary signals."

    return base_reasoning
