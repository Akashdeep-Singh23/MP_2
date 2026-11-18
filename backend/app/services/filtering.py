from typing import List, Dict, Any, Set

ALLOWED_DIFFICULTIES = {
    "Beginner": {"Beginner"},
    "Intermediate": {"Beginner", "Intermediate"},
    "Advanced": {"Beginner", "Intermediate", "Advanced"}
}

def is_difficulty_eligible(user_level: str, session_difficulty: str) -> bool:
    """
    Evaluates difficulty compatibility according to REC-05 / AT-01 - AT-03:
    Beginner -> Beginner only
    Intermediate -> Beginner + Intermediate
    Advanced -> Beginner + Intermediate + Advanced
    """
    allowed = ALLOWED_DIFFICULTIES.get(user_level, set())
    return session_difficulty in allowed

def is_equipment_eligible(user_equipment: List[str], required_equipment: List[str], alternatives_map: Dict[str, Set[str]] = None) -> bool:
    """
    Evaluates equipment availability according to EQ-01 - EQ-07 / AT-04:
    A session is eligible only if 100% of required equipment is in the user's available set,
    or satisfied by an explicitly approved alternative.
    """
    user_set = set(user_equipment)
    
    # Bodyweight execution check
    if not required_equipment or required_equipment == ["Bodyweight only"]:
        return "Bodyweight only" in user_set

    for item in required_equipment:
        if item in user_set:
            continue
        # Check if an alternative satisfies this item
        if alternatives_map and item in alternatives_map:
            alt_options = alternatives_map[item]
            if alt_options.intersection(user_set):
                continue
        # Item not satisfied
        return False

    return True

def apply_hard_filters(
    sessions: List[Dict[str, Any]],
    user_level: str,
    user_equipment: List[str],
    alternatives_map: Dict[str, Set[str]] = None
) -> List[Dict[str, Any]]:
    """
    Filters candidate workout sessions through mandatory hard eligibility constraints.
    Excluded records are never relaxed to fill the recommendation list.
    """
    eligible = []
    for session in sessions:
        # Check review status (DATA-06, DATA-07, AT-07)
        if session.get("review_status") != "approved":
            continue

        # Check duration verified (DATA-09, AT-06)
        duration = session.get("duration_minutes")
        if duration is None or duration <= 0:
            continue

        # Check difficulty compatibility (REC-05)
        difficulty = session.get("difficulty")
        if not is_difficulty_eligible(user_level, difficulty):
            continue

        # Check equipment compatibility (EQ-02)
        required_eq = session.get("required_equipment", [])
        if not is_equipment_eligible(user_equipment, required_eq, alternatives_map):
            continue

        eligible.append(session)

    return eligible
