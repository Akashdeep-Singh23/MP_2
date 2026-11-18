from typing import List, Dict, Any

def rank_sessions_baseline(
    eligible_sessions: List[Dict[str, Any]],
    user_profile: Dict[str, Any],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Deterministic Heuristic Baseline Ranker (SRS §6.4, PRD §18.2):
    Applies identical hard filters as Cosine ranker, but sorts strictly by:
    1. Primary-goal match
    2. Secondary-goal match
    3. Deterministic workout_id ASC tie-break
    """
    if not eligible_sessions:
        return []

    user_goal = user_profile.get("primary_goal", "").lower()

    scored = []
    for sess in eligible_sessions:
        primary_match = (sess.get("primary_goal", "").lower() == user_goal)
        secondary_match = any(sg.lower() == user_goal for sg in sess.get("secondary_goals", []))
        tier = 0 if primary_match else (1 if secondary_match else 2)

        item = dict(sess)
        item["_tier"] = tier
        scored.append(item)

    scored.sort(key=lambda s: (s["_tier"], s.get("workout_id", "")))

    results = scored[:top_k]
    for r in results:
        r.pop("_tier", None)

    return results
