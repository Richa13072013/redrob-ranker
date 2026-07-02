import argparse
import json
import csv
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from models import Candidate
from semantic import SemanticScorer
from scorer import score_candidate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", required=True, help="Path to output CSV")
    args = parser.parse_args()

    total_start = time.time()

    # Step 1: Load and parse all candidates
    print("Loading candidates...")
    start = time.time()
    all_candidates = []
    with open(args.candidates, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            all_candidates.append(Candidate.from_dict(d))
    print(f"  Loaded {len(all_candidates)} candidates in {time.time()-start:.1f}s")

    # Step 2: Fit semantic model on the full corpus
    print("Fitting semantic model...")
    start = time.time()
    semantic_scorer = SemanticScorer(n_components=100)
    all_texts = [c.career_text() for c in all_candidates]
    semantic_scorer.fit(all_texts)
    print(f"  Fitted in {time.time()-start:.1f}s")

    # Step 3: Batch semantic scoring
    print("Computing semantic scores...")
    start = time.time()
    sem_results = semantic_scorer.score_batch(all_texts)
    print(f"  Batch-scored in {time.time()-start:.1f}s")

    # Step 4: Composite scoring for every candidate
    print("Scoring candidates...")
    start = time.time()
    results = []
    for c, sem in zip(all_candidates, sem_results):
        r = score_candidate(c, precomputed_semantic=sem)
        results.append(r)
    print(f"  Scored in {time.time()-start:.1f}s")

    # Step 5: Sort — final_score descending, candidate_id ascending as tie-break
    results.sort(key=lambda r: (-r["final_score"], r["candidate_id"]))

    # Step 6: Take top 100
    top_100 = results[:100]

    # Step 7: Write CSV in the exact required format
    print(f"Writing {args.out}...")
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for i, r in enumerate(top_100, start=1):
            writer.writerow([
                r["candidate_id"],
                i,
                f"{r['final_score']:.4f}",
                r["reasoning"]
            ])

    total_elapsed = time.time() - total_start
    print(f"\nDone. Total runtime: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    print(f"Top 100 written to {args.out}")


if __name__ == "__main__":
    main()