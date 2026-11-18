import sys
import os
import json
import math
import asyncio
import argparse
from uuid import UUID

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.database import get_all_approved_sessions
from app.services.filtering import apply_hard_filters
from app.services.recommender import rank_sessions
from app.services.baseline import rank_sessions_baseline

def compute_dcg(relevances, k=5):
    dcg = 0.0
    for i, rel in enumerate(relevances[:k]):
        # DCG formula: (2^rel - 1) / log2(i + 2)
        dcg += (2.0 ** rel - 1.0) / math.log2(i + 2)
    return dcg

def compute_ndcg_at_5(ranked_sessions, labels_map):
    # Obtain relevance scores for the ranked order
    relevances = [labels_map.get(s["workout_id"], 0) for s in ranked_sessions]
    actual_dcg = compute_dcg(relevances, k=5)

    # Compute Ideal DCG (IDCG) by sorting labels in descending order
    ideal_relevances = sorted(labels_map.values(), reverse=True)
    idcg = compute_dcg(ideal_relevances, k=5)

    if idcg == 0:
        return 1.0  # Perfect score if all items are 0-relevance
    return actual_dcg / idcg

async def run_evaluation(labels_path):
    base_dir = os.path.dirname(__file__)
    profiles_path = os.path.join(base_dir, "..", "backend", "tests", "fixtures", "synthetic_profiles.json")
    with open(profiles_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    with open(labels_path, "r", encoding="utf-8") as f:
        labels_data = json.load(f)

    test_user_id = str(UUID("00000000-0000-0000-0000-000000000001"))
    sessions = await get_all_approved_sessions(test_user_id)
    if not sessions:
        raise RuntimeError("No approved database sessions are available for evaluation.")
    session_ids = {session["workout_id"] for session in sessions}

    print("================================================================================")
    print("             ML RANKING BENCHMARK EVALUATION (NDCG@5 vs BASELINE)              ")
    print("================================================================================")
    print(f"Total Synthetic Profiles Evaluated: {len(profiles)}")
    print(f"Total Approved Sessions in Pool:   {len(sessions)}")
    print("--------------------------------------------------------------------------------")
    print(f"{'Profile ID':<10} | {'Profile Name':<32} | {'Cosine NDCG@5':<13} | {'Baseline NDCG@5':<14}")
    print("--------------------------------------------------------------------------------")

    cosine_scores = []
    baseline_scores = []

    for p in profiles:
        p_id = p["id"]
        # Skip active hold profiles from ranking comparison
        if p.get("hold"):
            print(f"{p_id:<10} | {p['name']:<32} | {'[SAFETY HOLD]':<13} | {'[SAFETY HOLD]':<14}")
            continue

        prof_dict = {
            "primary_goal": p["goal"],
            "fitness_level": p["level"],
            "equipment": p["equipment"],
            "available_duration_minutes": p["duration"]
        }

        # Apply identical hard filters
        eligible = apply_hard_filters(
            sessions,
            user_level=p["level"],
            user_equipment=p["equipment"]
        )

        labels_map = labels_data.get(p_id, {})
        if not session_ids.intersection(labels_map):
            raise RuntimeError(
                f"Relevance labels for {p_id} do not cover any current approved workout IDs; relabel the current catalogue."
            )

        # Rank with Cosine
        cosine_ranked = rank_sessions(eligible, prof_dict, top_k=5)
        cosine_ndcg = compute_ndcg_at_5(cosine_ranked, labels_map)

        # Rank with Baseline
        baseline_ranked = rank_sessions_baseline(eligible, prof_dict, top_k=5)
        baseline_ndcg = compute_ndcg_at_5(baseline_ranked, labels_map)

        cosine_scores.append(cosine_ndcg)
        baseline_scores.append(baseline_ndcg)

        print(f"{p_id:<10} | {p['name']:<32} | {cosine_ndcg:<13.4f} | {baseline_ndcg:<14.4f}")

    print("================================================================================")
    avg_cosine = sum(cosine_scores) / len(cosine_scores) if cosine_scores else 0.0
    avg_baseline = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0
    print(f"Mean NDCG@5 (Cosine Similarity): {avg_cosine:.4f}")
    print(f"Mean NDCG@5 (Baseline Ranker):   {avg_baseline:.4f}")
    print("================================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate ranking against reviewer-provided relevance labels.")
    parser.add_argument("--labels", required=True, help="JSON labels for the current approved workout catalogue")
    args = parser.parse_args()
    try:
        asyncio.run(run_evaluation(args.labels))
    except Exception as error:
        print(f"Evaluation could not run: {error}", file=sys.stderr)
        raise SystemExit(2)
