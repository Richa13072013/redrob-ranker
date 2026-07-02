# Redrob Ranker — AI Candidate Ranking System

A hybrid scoring system that ranks 100,000 candidate profiles for a Senior AI Engineer
role, combining structured feature scoring with semantic similarity and behavioral
signals — built to resist keyword-stuffing and reward genuine career substance over
jargon density.

## Approach

Rather than pure keyword matching or a single embedding similarity score, this system
scores each candidate across five independent signal types and combines them into a
weighted composite:

| Signal | What it measures | Weight |
|---|---|---|
| Title match | Career trajectory relevance (current + past titles) | 25% |
| Skill evidence | Claimed skills cross-checked against career history text (not just listed) | 20% |
| Semantic similarity | Career narrative compared against two "ideal candidate" profiles (shipper / technical) using TF-IDF+SVD | 20% |
| Experience band | Fit within the 5-9 year target range | 15% |
| Location fit | Pune/Noida proximity and relocation willingness | 12% |
| Education tier | Institution tier as a minor tiebreaker signal | 8% |

This base score is then:
1. **Suppressed** (not excluded) by a disqualifier multiplier if honeypot patterns or
   JD-stated hard exclusions are detected
2. **Modulated** by a behavioral multiplier from `redrob_signals` (availability,
   engagement, salary fit)

## Why hybrid, not pure embeddings or pure keywords

Pure keyword/skill matching falls for the keyword-stuffing trap (a candidate listing
"LoRA, RAG, Pinecone" as skills with zero evidence of using them). Pure embedding
similarity on the full profile text has the same problem — a skills-padded profile
still produces high cosine similarity. Structured scoring on distinct fields (title vs
skills vs semantic narrative vs location) means each trap type is caught by the
specific signal built to catch it.

## Semantic layer: two narratives, not one

The JD explicitly wants candidates who are strong at both production shipping AND
technical depth. A single "ideal candidate" narrative would blur this into one
opinionated voice. Instead, career text is compared against two separate narratives —
a "shipper" profile and a "technical depth" profile — and blended 60/40 in favor of
shipping, matching the JD's stated preference to "tilt slightly toward shipper."

## Honeypot / disqualifier handling

Suspicious profiles (e.g. "expert" skill proficiency with 0 months usage, or claimed
experience far exceeding actual career history span) and JD-stated hard exclusions
(consulting-only career history, pure-research-only background) are **suppressed, not
excluded**. This is intentional: rule-based detection is imperfect, so a heavy
suppression multiplier (0.05-0.20x) still allows an exceptional candidate to claw back
into contention if every other signal strongly disagrees with the flag, while
reliably burying genuinely weak/synthetic profiles.

## How to run

```bash
pip install -r requirements.txt
python rank.py --candidates ./data/candidates.jsonl --out ./output/submission.csv
```

Runtime: ~80 seconds on a standard CPU laptop (no GPU, no network) for 100,000
candidates. Well within the 5-minute budget.

## Validate output

```bash
python data/validate_submission.py output/submission.csv
```

## Project structure

```
src/
  models.py        - typed data classes for parsing candidate JSON
  disqualifiers.py - honeypot detection + hard JD disqualifiers
  features.py       - structured scoring (title, skills, location, experience, education)
  narratives.py     - the two "ideal candidate" text narratives
  semantic.py       - TF-IDF+SVD semantic similarity scorer
  behavioral.py     - redrob_signals-based availability/engagement/salary scoring
  scorer.py          - combines all signals into final composite score + reasoning
rank.py             - end-to-end pipeline: load, score, rank, write submission CSV
```

## Known limitations

- Honeypot detection currently catches ~46 of an estimated ~80 synthetic honeypots
  via two heuristics (expert-skill-with-zero-usage, experience-span mismatch). There
  are likely 1-2 additional honeypot signature types not yet isolated. The suppression
  approach (rather than hard exclusion) is designed to be robust to this gap.
- No ground-truth relevance labels exist for this challenge, so scoring weights were
  tuned against the JD's stated intent and manually-verified strong/weak candidates,
  not against a labeled validation set.
- The README in the original data bundle references `candidates.jsonl.gz`, but the
  delivered file is plain `.jsonl` (no compression) — noted here for transparency.

## AI tools used

Claude was used for architecture discussion, code review, and debugging throughout
development. No candidate data was sent to any external LLM API — all scoring runs
locally with no network access, per the compute constraints.
