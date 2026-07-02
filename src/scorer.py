from models import Candidate
from disqualifiers import combined_suppression
from features import (title_score, skill_evidence_score,
                      experience_band_score, location_score, education_score)
from behavioral import behavioral_multiplier


def score_candidate(c: Candidate, precomputed_semantic: dict = None) -> dict:

    # Step 1: check disqualifiers
    dq = combined_suppression(c)

    # Step 2: structured features
    ts = title_score(c)
    se = skill_evidence_score(c)
    eb = experience_band_score(c)
    ls = location_score(c)
    ed = education_score(c)

    # Step 2b: semantic similarity (precomputed in a batch upstream, for speed)
    if precomputed_semantic is not None:
        sem = precomputed_semantic
        sem_score = sem["semantic_score"]
    else:
        sem_score = 0.0
        sem = {"shipper_sim": 0.0, "technical_sim": 0.0, "semantic_score": 0.0}

    # Step 3: weighted composite
    base_score = (
        0.25 * ts +
        0.20 * se +
        0.20 * sem_score +
        0.15 * eb +
        0.12 * ls +
        0.08 * ed
    )
    # Step 4: apply disqualifier suppression
    suppressed_score = base_score * dq.multiplier

    # Step 5: behavioral multiplier
    beh_mult, beh_components = behavioral_multiplier(c)

    # Step 6: final score
    final_score = suppressed_score * beh_mult

    # Step 7: build reasoning string
    reasoning = build_reasoning(c, ts, se, eb, ls, ed, dq, beh_components)

    return {
        "candidate_id": c.candidate_id,
        "final_score": round(final_score, 4),
        "base_score": round(base_score, 4),
        "disqualifier_multiplier": dq.multiplier,
        "behavioral_multiplier": beh_mult,
        "title_score": round(ts, 3),
        "skill_score": round(se, 3),
        "experience_score": round(eb, 3),
        "location_score": round(ls, 3),
        "education_score": round(ed, 3),
        "disqualifier_reasons": dq.reasons,
        "behavioral": beh_components,
        "semantic_score": round(sem_score, 3),
        "shipper_sim": sem["shipper_sim"],
        "technical_sim": sem["technical_sim"],
        "reasoning": reasoning
    }


def build_reasoning(c, ts, se, eb, ls, ed, dq, beh) -> str:
    parts = []

    # Title signal
    if ts >= 0.90:
        parts.append(f"{c.profile.current_title} is a direct title match")
    elif ts >= 0.60:
        parts.append(f"{c.profile.current_title} is an adjacent AI/ML role")
    elif ts > 0:
        parts.append(f"{c.profile.current_title} is a general tech role with some relevance")
    else:
        parts.append(f"{c.profile.current_title} is not a relevant title")

    # Experience
    yoe = c.profile.years_of_experience
    parts.append(f"{yoe}y experience")

    # Skills
    if se >= 0.50:
        parts.append("strong evidenced skill match")
    elif se >= 0.25:
        parts.append("moderate skill match")
    elif se > 0:
        parts.append("weak skill match")
    else:
        parts.append("no relevant skills")

    # Location
    loc = c.profile.location
    willing = c.redrob_signals.willing_to_relocate if c.redrob_signals else False
    if ls >= 0.99:
        parts.append(f"based in {loc} (target location)")
    elif ls >= 0.80:
        parts.append(f"based in {loc} (nearby city)")
    elif willing:
        parts.append(f"based in {loc}, willing to relocate")
    else:
        parts.append(f"based in {loc}, not willing to relocate")

    # Behavioral
    rr = beh.get("engagement", 0)
    if rr >= 0.70:
        parts.append("high engagement score")
    elif rr >= 0.40:
        parts.append("moderate engagement score")
    else:
        parts.append("low engagement score")

    # Disqualifiers
    if dq.reasons:
        parts.append("FLAG: " + "; ".join(dq.reasons))

    return ". ".join(parts) + "."