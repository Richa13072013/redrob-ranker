from dataclasses import dataclass
from datetime import date
from models import Candidate

TODAY = date(2026, 6, 29)

CONSULTING_FIRMS = {
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "tata consultancy services"
}

@dataclass
class DisqualifierResult:
    multiplier: float
    reasons: list
def check_honeypot(c: Candidate) -> DisqualifierResult:
    reasons = []
    multiplier = 1.0

    # Check 1: expert proficiency with 0 months usage
    for s in c.skills:
        if s.proficiency == "expert" and (s.duration_months or 0) == 0:
            reasons.append(f"honeypot: expert in {s.name} with 0 months usage")
            multiplier = min(multiplier, 0.05)
            break

    # Check 2: claimed experience far exceeds career history span
    starts = [j.start_date for j in c.career_history if j.start_date]
    if starts:
        earliest = min(starts)
        span_years = (TODAY - earliest).days / 365.25
        if c.profile.years_of_experience > span_years + 1.5:
            reasons.append(
                f"honeypot: claims {c.profile.years_of_experience}y experience "
                f"but career history only spans {span_years:.1f}y"
            )
            multiplier = min(multiplier, 0.05)

    return DisqualifierResult(multiplier=multiplier, reasons=reasons)

def check_hard_disqualifiers(c: Candidate) -> DisqualifierResult:
    reasons = []
    multiplier = 1.0

    # Build full text from career history for searching
    parts = [c.profile.summary, c.profile.headline]
    parts += [j.description for j in c.career_history]
    parts += [j.title for j in c.career_history]
    text = " ".join(parts).lower()

    # Check 1: consulting-only career history
    companies = {j.company.lower() for j in c.career_history}
    if companies and companies.issubset(CONSULTING_FIRMS):
        reasons.append("consulting-only career history, no product company stint")
        multiplier = min(multiplier, 0.20)

    # Check 2: pure research, no production signal
    research_markers = ["research lab", "academic", "phd researcher", "postdoc"]
    production_markers = ["production", "shipped", "deployed", "live", "scale", "launched"]
    has_research = any(m in text for m in research_markers)
    has_production = any(m in text for m in production_markers)
    if has_research and not has_production:
        reasons.append("research-only background, no production deployment signal")
        multiplier = min(multiplier, 0.15)

    return DisqualifierResult(multiplier=multiplier, reasons=reasons)

def combined_suppression(c: Candidate) -> DisqualifierResult:
    hp = check_honeypot(c)
    dq = check_hard_disqualifiers(c)
    all_reasons = hp.reasons + dq.reasons
    mult = min(hp.multiplier, dq.multiplier)
    return DisqualifierResult(multiplier=mult, reasons=all_reasons)