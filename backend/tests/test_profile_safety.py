import pytest
from tests.conftest import create_test_access_token

def test_profile_requires_auth(client):
    # AT-18: Reject request with missing token
    response = client.get("/api/profile")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "MISSING_TOKEN"

def test_profile_rejects_invalid_token(client):
    # AT-18: Reject token that Supabase Auth cannot validate
    token = create_test_access_token("invalid-user", invalid=True)
    response = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "INVALID_TOKEN"

def test_profile_save_and_retrieve_success(client, auth_headers):
    payload = {
        "primary_goal": "Muscle gain",
        "fitness_level": "Intermediate",
        "equipment": ["Dumbbells", "Bench"],
        "available_duration_minutes": 45,
        "screening_answers": {
            "has_active_injury": False,
            "has_ongoing_limitation": False,
            "has_current_pain": False,
            "has_urgent_symptoms": False
        },
        "confirm_cleared": True
    }
    # Update profile
    put_res = client.put("/api/profile", json=payload, headers=auth_headers)
    assert put_res.status_code == 200
    saved = put_res.json()
    assert saved["primary_goal"] == "Muscle gain"
    assert saved["safety_hold"] is False
    assert saved["safety_screening_status"] == "CLEARED"

    # Read profile
    get_res = client.get("/api/profile", headers=auth_headers)
    assert get_res.status_code == 200
    read = get_res.json()
    assert read["primary_goal"] == "Muscle gain"
    assert read["equipment"] == ["Dumbbells", "Bench"]

def test_profile_rejects_empty_equipment(client, auth_headers):
    # AT-05: Empty equipment selection is rejected
    payload = {
        "primary_goal": "Muscle gain",
        "fitness_level": "Intermediate",
        "equipment": [],
        "available_duration_minutes": 45,
        "screening_answers": {},
        "confirm_cleared": True
    }
    res = client.put("/api/profile", json=payload, headers=auth_headers)
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"

def test_safety_hold_blocks_recommendations(client, auth_headers):
    # AT-08: Active safety hold blocks recommendations with HTTP 409
    payload = {
        "primary_goal": "Fat loss",
        "fitness_level": "Beginner",
        "equipment": ["Bodyweight only"],
        "available_duration_minutes": 30,
        "screening_answers": {
            "has_active_injury": True,
            "has_ongoing_limitation": False,
            "has_current_pain": False,
            "has_urgent_symptoms": False
        },
        "confirm_cleared": False
    }
    client.put("/api/profile", json=payload, headers=auth_headers)

    # Attempt to request recommendations
    rec_res = client.post("/api/recommendations", headers=auth_headers)
    assert rec_res.status_code == 409
    data = rec_res.json()
    assert data["error"]["code"] == "SAFETY_HOLD_ACTIVE"

def test_changing_goal_does_not_bypass_hold(client, auth_headers):
    # AT-09: Changing goal/equipment does not bypass hold without resolving screening
    payload = {
        "primary_goal": "Endurance",
        "fitness_level": "Beginner",
        "equipment": ["Bodyweight only"],
        "available_duration_minutes": 30,
        "screening_answers": {
            "has_active_injury": True
        },
        "confirm_cleared": False
    }
    client.put("/api/profile", json=payload, headers=auth_headers)

    # Change goal to Flexibility
    payload["primary_goal"] = "Flexibility and mobility"
    client.put("/api/profile", json=payload, headers=auth_headers)

    rec_res = client.post("/api/recommendations", headers=auth_headers)
    assert rec_res.status_code == 409
    assert rec_res.json()["error"]["code"] == "SAFETY_HOLD_ACTIVE"

def test_urgent_symptoms_guidance(client, auth_headers):
    # AT-10: Urgent symptoms trigger emergency state
    payload = {
        "primary_goal": "General fitness",
        "fitness_level": "Beginner",
        "equipment": ["Bodyweight only"],
        "available_duration_minutes": 30,
        "screening_answers": {
            "has_urgent_symptoms": True
        },
        "confirm_cleared": False
    }
    res = client.put("/api/profile", json=payload, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["safety_screening_status"] == "URGENT_SYMPTOMS"
    assert res.json()["safety_hold"] is True
