import numpy as np
from typing import Dict, Any, List

GOALS_LIST = [
    "Muscle gain",
    "Fat loss",
    "Endurance",
    "General fitness",
    "Strength improvement",
    "Flexibility and mobility"
]

WORKOUT_TYPES = [
    "Strength",
    "Cardio",
    "Plyometrics",
    "Stretching"
]

MUSCLE_GROUPS = [
    "Chest",
    "Back",
    "Legs",
    "Shoulders",
    "Arms",
    "Core",
    "Full Body",
    "Cardio/Systemic"
]

MUSCLE_TO_GROUP = {
    "chest": "Chest", "pectorals": "Chest",
    "back": "Back", "lats": "Back", "latissimus dorsi": "Back",
    "middle back": "Back", "lower back": "Back", "traps": "Back", "trapezius": "Back",
    "legs": "Legs", "quadriceps": "Legs", "hamstrings": "Legs", "calves": "Legs",
    "glutes": "Legs", "adductors": "Legs", "abductors": "Legs",
    "shoulders": "Shoulders", "deltoids": "Shoulders",
    "arms": "Arms", "biceps": "Arms", "triceps": "Arms", "forearms": "Arms",
    "core": "Core", "abdominals": "Core", "abs": "Core",
    "full body": "Full Body", "cardio/systemic": "Cardio/Systemic",
}

def build_profile_vector(profile: Dict[str, Any]) -> np.ndarray:
    """
    Constructs a normalized 19-dimensional feature vector for a user profile:
    - 6 dims: Primary Goal (one-hot)
    - 4 dims: Implied Workout Type preferences based on primary goal
    - 8 dims: Implied Primary Target Muscle preferences based on primary goal
    - 1 dim: Target duration normalized (1.0)
    """
    vec = []
    
    # 1. Goal subspace (6 dims)
    user_goal = profile.get("primary_goal", "")
    for goal in GOALS_LIST:
        vec.append(1.0 if user_goal.lower() == goal.lower() else 0.0)

    # 2. Workout type subspace (4 dims)
    goal_to_type = {
        "muscle gain": "Strength",
        "strength improvement": "Strength",
        "fat loss": "Cardio",
        "endurance": "Cardio",
        "flexibility and mobility": "Stretching",
        "general fitness": "Strength"
    }
    preferred_type = goal_to_type.get(user_goal.lower(), "Strength")
    for wt in WORKOUT_TYPES:
        vec.append(1.0 if preferred_type.lower() == wt.lower() else 0.0)

    # 3. Muscle group subspace (8 dims); goals without a specific muscle focus use a balanced prior.
    goal_muscles = {
        "muscle gain": {"Chest", "Back", "Legs", "Shoulders", "Arms"},
        "strength improvement": {"Chest", "Back", "Legs", "Shoulders", "Arms"},
        "fat loss": {"Legs", "Core", "Full Body", "Cardio/Systemic"},
        "endurance": {"Legs", "Core", "Full Body", "Cardio/Systemic"},
        "flexibility and mobility": {"Back", "Legs", "Shoulders", "Core"},
        "general fitness": set(MUSCLE_GROUPS),
    }
    preferred_muscles = goal_muscles.get(user_goal.lower(), set(MUSCLE_GROUPS))
    for mg in MUSCLE_GROUPS:
        vec.append(1.0 if mg in preferred_muscles else 0.0)

    # 4. Normalized duration baseline (1.0)
    vec.append(1.0)

    arr = np.array(vec, dtype=float)
    norm = np.linalg.norm(arr)
    return arr / norm if norm > 0 else arr

def build_session_vector(session: Dict[str, Any], user_duration_minutes: int) -> np.ndarray:
    """
    Constructs a 19-dimensional feature vector for a workout session:
    - 6 dims: Primary Goal (one-hot)
    - 4 dims: Workout Type (one-hot)
    - 8 dims: Primary Target Muscles in session exercises (multi-hot)
    - 1 dim: Normalized duration fit relative to user's time budget
    """
    vec = []

    # 1. Goal subspace (6 dims)
    sess_goal = session.get("primary_goal", "")
    for goal in GOALS_LIST:
        vec.append(1.0 if sess_goal.lower() == goal.lower() else 0.0)

    # 2. Workout type subspace (4 dims)
    sess_type = session.get("workout_type", "")
    for wt in WORKOUT_TYPES:
        vec.append(1.0 if sess_type.lower() == wt.lower() else 0.0)

    # 3. Muscle group subspace (8 dims)
    session_muscles = set()
    for ex in session.get("exercises", []):
        for m in ex.get("primary_muscles", []):
            group = MUSCLE_TO_GROUP.get(str(m).strip().lower())
            if group:
                session_muscles.add(group)
    
    for mg in MUSCLE_GROUPS:
        vec.append(1.0 if mg in session_muscles else 0.0)

    # 4. Normalized duration fit (1 dim)
    sess_duration = session.get("duration_minutes", 30)
    if user_duration_minutes > 0 and sess_duration > 0:
        duration_ratio = min(sess_duration, user_duration_minutes) / max(sess_duration, user_duration_minutes)
    else:
        duration_ratio = 0.5
    vec.append(duration_ratio)

    arr = np.array(vec, dtype=float)
    norm = np.linalg.norm(arr)
    return arr / norm if norm > 0 else arr
