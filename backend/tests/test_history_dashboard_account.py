import pytest
from tests.conftest import create_test_access_token

def test_explicit_completion_at19_and_deduplication_at20(client):
    token = create_test_access_token("user-completion-test")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "workout_id": "session-mg-01",
        "idempotency_key": "unique-idemp-key-1"
    }

    # AT-19: Explicit completion created
    res1 = client.post("/api/history", json=payload, headers=headers)
    assert res1.status_code == 201
    item1 = res1.json()
    assert item1["workout_id"] == "session-mg-01"

    # AT-20: Repeated submission with same idempotency key returns existing entry
    res2 = client.post("/api/history", json=payload, headers=headers)
    assert res2.status_code == 201
    item2 = res2.json()
    assert item2["id"] == item1["id"]

    # History list should contain exactly 1 entry
    hist_res = client.get("/api/history", headers=headers)
    assert hist_res.status_code == 200
    assert hist_res.json()["total_count"] == 1

def test_dashboard_aggregations_at21(client):
    token = create_test_access_token("user-dashboard-test")
    headers = {"Authorization": f"Bearer {token}"}

    # Log 2 completions
    client.post("/api/history", json={"workout_id": "session-mg-01", "idempotency_key": "k1"}, headers=headers)
    client.post("/api/history", json={"workout_id": "session-fl-01", "idempotency_key": "k2"}, headers=headers)

    dash_res = client.get("/api/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash = dash_res.json()
    assert dash["total_completed"] == 2
    assert len(dash["recent_activity"]) == 2
    assert dash["goal_wise_counts"]["Muscle gain"] >= 1
    assert dash["goal_wise_counts"]["Fat loss"] >= 1
    assert len(dash["weekly_trends"]) >= 1

def test_user_data_isolation_at17(client):
    # AT-17: User A cannot read User B's history
    token_a = create_test_access_token("user-alpha")
    token_b = create_test_access_token("user-bravo")

    # User A logs a workout
    client.post("/api/history", json={"workout_id": "session-mg-01", "idempotency_key": "a1"}, headers={"Authorization": f"Bearer {token_a}"})

    # User B reads history - should be empty
    res_b = client.get("/api/history", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    assert res_b.json()["total_count"] == 0

def test_account_deletion_at22(client):
    # AT-22: Account deletion purges profile and history
    token = create_test_access_token("user-delete-me")
    headers = {"Authorization": f"Bearer {token}"}

    # Create profile and history
    client.put("/api/profile", json={
        "primary_goal": "Endurance",
        "fitness_level": "Beginner",
        "equipment": ["Bodyweight only"],
        "available_duration_minutes": 30,
        "screening_answers": {},
        "confirm_cleared": True
    }, headers=headers)
    client.post("/api/history", json={"workout_id": "session-end-01", "idempotency_key": "del-1"}, headers=headers)

    # Delete account
    del_res = client.request("DELETE", "/api/account", json={"confirmation": "DELETE_MY_ACCOUNT"}, headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # Deleted account tokens are no longer accepted by Supabase Auth.
    prof_res = client.get("/api/profile", headers=headers)
    assert prof_res.status_code == 401

    # History is likewise unavailable after the identity is deleted.
    hist_res = client.get("/api/history", headers=headers)
    assert hist_res.status_code == 401

def test_nutrition_guidance_at23(client):
    # AT-23: General guidance without prohibited meal plans/calorie targets
    res = client.get("/api/nutrition")
    assert res.status_code == 200
    data = res.json()
    assert "disclaimer" in data
    assert "topics" in data
    text_content = str(data)
    assert "calorie deficit" not in text_content.lower()
    assert "therapeutic diet" not in text_content.lower()
