from datetime import date
from models import Candidate

TODAY = date(2026, 6, 29)
JD_SALARY_MIN = 30.0
JD_SALARY_MAX = 55.0


def availability_score(c: Candidate) -> float:
    s = c.redrob_signals
    if not s:
        return 0.5
    score = 0.0

    if s.open_to_work_flag:
        score += 0.40

    if s.last_active_date:
        days = (TODAY - s.last_active_date).days
        if days <= 30:
            score += 0.30
        elif days <= 90:
            score += 0.20
        elif days <= 180:
            score += 0.10

    if s.notice_period_days <= 30:
        score += 0.20
    elif s.notice_period_days <= 60:
        score += 0.10
    elif s.notice_period_days <= 90:
        score += 0.05

    if s.verified_email and s.verified_phone:
        score += 0.10

    return min(score, 1.0)


def engagement_score(c: Candidate) -> float:
    s = c.redrob_signals
    if not s:
        return 0.5
    score = 0.0

    score += 0.40 * s.recruiter_response_rate

    if s.interview_completion_rate >= 0:
        score += 0.25 * s.interview_completion_rate

    if s.github_activity_score >= 0:
        score += 0.20 * min(s.github_activity_score / 10.0, 1.0)

    score += 0.15 * min(s.saved_by_recruiters_30d / 10.0, 1.0)

    return min(score, 1.0)


def salary_fit_score(c: Candidate) -> float:
    s = c.redrob_signals
    if not s:
        return 0.7
    lo = s.expected_salary_min_lpa
    hi = s.expected_salary_max_lpa
    if lo == 0 and hi == 0:
        return 0.7
    overlap = max(0, min(hi, JD_SALARY_MAX) - max(lo, JD_SALARY_MIN))
    if overlap > 0:
        return 1.0
    gap = max(lo - JD_SALARY_MAX, JD_SALARY_MIN - hi)
    return max(0.3, 1.0 - gap / 20.0)


def behavioral_multiplier(c: Candidate) -> tuple:
    avail = availability_score(c)
    engage = engagement_score(c)
    salary = salary_fit_score(c)

    raw = 0.45 * engage + 0.35 * avail + 0.20 * salary
    multiplier = 0.50 + 0.50 * raw

    components = {
        "availability": round(avail, 3),
        "engagement": round(engage, 3),
        "salary_fit": round(salary, 3)
    }
    return round(multiplier, 4), components
