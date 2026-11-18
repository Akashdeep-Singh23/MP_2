import pytest
import numpy as np
from app.services.filtering import is_difficulty_eligible, is_equipment_eligible, apply_hard_filters
from app.services.recommender import compute_cosine_similarity, rank_sessions, generate_explanations

def test_difficulty_mapping_at01_to_at03():
    # AT-01: Beginner never receives Intermediate or Advanced
    assert is_difficulty_eligible("Beginner", "Beginner") is True
    assert is_difficulty_eligible("Beginner", "Intermediate") is False
    assert is_difficulty_eligible("Beginner", "Advanced") is False

    # AT-02: Intermediate receives Beginner + Intermediate, never Advanced
    assert is_difficulty_eligible("Intermediate", "Beginner") is True
    assert is_difficulty_eligible("Intermediate", "Intermediate") is True
    assert is_difficulty_eligible("Intermediate", "Advanced") is False

    # AT-03: Advanced receives all three levels
    assert is_difficulty_eligible("Advanced", "Beginner") is True
    assert is_difficulty_eligible("Advanced", "Intermediate") is True
    assert is_difficulty_eligible("Advanced", "Advanced") is True

def test_equipment_eligibility_at04():
    # AT-04: Session requiring unavailable equipment is excluded
    user_eq = ["Dumbbells", "Bench"]
    assert is_equipment_eligible(user_eq, ["Dumbbells"]) is True
    assert is_equipment_eligible(user_eq, ["Dumbbells", "Bench"]) is True
    assert is_equipment_eligible(user_eq, ["Barbell"]) is False
    assert is_equipment_eligible(user_eq, ["Dumbbells", "Cable machine"]) is False

def test_unapproved_and_invalid_records_excluded_at06_at07():
    candidates = [
        {"workout_id": "s1", "review_status": "approved", "duration_minutes": 30, "difficulty": "Beginner", "required_equipment": ["Bodyweight only"]},
        {"workout_id": "s2", "review_status": "quarantined", "duration_minutes": 30, "difficulty": "Beginner", "required_equipment": ["Bodyweight only"]}, # AT-07
        {"workout_id": "s3", "review_status": "approved", "duration_minutes": 0, "difficulty": "Beginner", "required_equipment": ["Bodyweight only"]}, # AT-06
    ]
    eligible = apply_hard_filters(candidates, user_level="Beginner", user_equipment=["Bodyweight only"])
    ids = [s["workout_id"] for s in eligible]
    assert "s1" in ids
    assert "s2" not in ids
    assert "s3" not in ids

def test_zero_vector_and_robustness_at15():
    # AT-15: Zero-vector or undefined similarity handles gracefully
    zero_vec = np.zeros(19)
    normal_vec = np.ones(19)
    sim = compute_cosine_similarity(zero_vec, normal_vec)
    assert sim == 0.0
    assert not np.isnan(sim)
    assert not np.isinf(sim)

def test_determinism_at14():
    # AT-14: Identical inputs produce identical ordered results
    profile = {
        "primary_goal": "Muscle gain",
        "fitness_level": "Intermediate",
        "equipment": ["Dumbbells", "Bench", "Bodyweight only"],
        "available_duration_minutes": 45
    }
    candidates = [
        {"workout_id": "w1", "primary_goal": "Muscle gain", "difficulty": "Intermediate", "duration_minutes": 45, "required_equipment": ["Dumbbells"], "workout_type": "Strength", "review_status": "approved"},
        {"workout_id": "w2", "primary_goal": "Muscle gain", "difficulty": "Beginner", "duration_minutes": 30, "required_equipment": ["Bodyweight only"], "workout_type": "Strength", "review_status": "approved"},
    ]
    res1 = rank_sessions(candidates, profile, top_k=5)
    res2 = rank_sessions(candidates, profile, top_k=5)

    assert [r["workout_id"] for r in res1] == [r["workout_id"] for r in res2]
    assert [r["similarity_score"] for r in res1] == [r["similarity_score"] for r in res2]

def test_recommendation_cap_at13():
    # AT-13: Max 5 results returned
    profile = {"primary_goal": "General fitness", "fitness_level": "Advanced", "equipment": ["Bodyweight only"], "available_duration_minutes": 30}
    candidates = [
        {"workout_id": f"w{i}", "primary_goal": "General fitness", "difficulty": "Beginner", "duration_minutes": 30, "required_equipment": ["Bodyweight only"], "workout_type": "Strength", "review_status": "approved"}
        for i in range(10)
    ]
    res = rank_sessions(candidates, profile, top_k=5)
    assert len(res) == 5

def test_explanations_contain_verified_data_at16():
    # AT-16: Explanations cite verified profile and session attributes
    profile = {"primary_goal": "Muscle gain", "fitness_level": "Intermediate", "available_duration_minutes": 45}
    session = {"primary_goal": "Muscle gain", "difficulty": "Intermediate", "duration_minutes": 45, "required_equipment": ["Dumbbells"]}
    reasons, caution = generate_explanations(session, profile)

    assert any("Muscle gain" in r for r in reasons)
    assert any("Intermediate" in r for r in reasons)
    assert any("Dumbbells" in r for r in reasons)
    assert caution is None
