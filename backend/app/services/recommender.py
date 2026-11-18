import numpy as np
from typing import List, Dict, Any, Tuple
from app.services.vectorizer import build_profile_vector, build_session_vector

def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Computes Cosine Similarity between two vectors with explicit safeguards
    for zero vectors, NaN, and Infinity (REC-11, AT-15).
    """
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    dot = np.dot(vec_a, vec_b)
    sim = dot / (norm_a * norm_b)

    if np.isnan(sim) or np.isneginf(sim) or np.isposinf(sim):
        return 0.0

    return float(np.clip(sim, 0.0, 1.0))

def generate_explanations(session: Dict[str, Any], user_profile: Dict[str, Any]) -> Tuple[List[str], str]:
    """
    Generates transparent, evidence-based match reasons citing verified data (REC-16, AT-16).
    """
    reasons = []
    user_goal = user_profile.get("primary_goal")
    sess_goal = session.get("primary_goal")
    user_level = user_profile.get("fitness_level")
    sess_diff = session.get("difficulty")
    user_dur = user_profile.get("available_duration_minutes", 45)
    sess_dur = session.get("duration_minutes", 30)

    # Goal alignment
    if user_goal.lower() == sess_goal.lower():
        reasons.append(f"Directly matches your primary goal of '{user_goal}'.")
    elif user_goal in session.get("secondary_goals", []):
        reasons.append(f"Supports your secondary fitness focus in '{user_goal}'.")

    # Difficulty alignment
    reasons.append(f"Difficulty level '{sess_diff}' is suitable for your '{user_level}' fitness level.")

    # Equipment verification
    req_eq = session.get("required_equipment", [])
    if req_eq:
        eq_str = ", ".join(req_eq)
        reasons.append(f"All required equipment ({eq_str}) is confirmed available in your equipment inventory.")
    else:
        reasons.append("Designed for bodyweight execution; no specialized equipment needed.")

    # Duration fit & caution
    duration_caution = None
    if sess_dur <= user_dur:
        reasons.append(f"Estimated duration ({sess_dur} mins) fits within your available time ({user_dur} mins).")
    else:
        diff = sess_dur - user_dur
        duration_caution = f"Session exceeds your available time budget by {diff} minutes."
        reasons.append(f"Estimated duration is {sess_dur} minutes ({diff} mins longer than preferred).")

    return reasons, duration_caution

def rank_sessions(
    eligible_sessions: List[Dict[str, Any]],
    user_profile: Dict[str, Any],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Ranks eligible workout sessions using Content-Based Cosine Similarity:
    1. Primary-goal match tier > Secondary-goal match tier > Other tier
    2. Cosine Similarity score DESC
    3. Deterministic workout_id ASC tie-break
    Capped at top_k (default 5).
    """
    if not eligible_sessions:
        return []

    user_vec = build_profile_vector(user_profile)
    user_goal = user_profile.get("primary_goal", "").lower()
    user_dur = user_profile.get("available_duration_minutes", 45)

    scored_sessions = []
    for sess in eligible_sessions:
        sess_vec = build_session_vector(sess, user_dur)
        sim = compute_cosine_similarity(user_vec, sess_vec)

        # Determine priority tier (REC-08)
        primary_match = (sess.get("primary_goal", "").lower() == user_goal)
        secondary_match = any(sg.lower() == user_goal for sg in sess.get("secondary_goals", []))
        
        tier = 0 if primary_match else (1 if secondary_match else 2)

        explanations, caution = generate_explanations(sess, user_profile)

        # Attach computed fields
        enriched = dict(sess)
        enriched["similarity_score"] = round(sim, 4)
        enriched["duration_caution"] = caution
        enriched["match_explanations"] = explanations
        enriched["_tier"] = tier

        scored_sessions.append(enriched)

    # Deterministic multi-key sort:
    # 1. Tier ASC (0 is highest priority)
    # 2. Similarity Score DESC (-score)
    # 3. workout_id ASC for stable tie-break (REC-12, REC-18, AT-14)
    scored_sessions.sort(key=lambda s: (s["_tier"], -s["similarity_score"], s.get("workout_id", "")))

    # Truncate to top_k (REC-13)
    results = scored_sessions[:top_k]

    # Clean up internal sorting key
    for r in results:
        r.pop("_tier", None)

    return results
