# API.md — REST Interface Specification & Contract Catalog

**Project:** Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning  
**Version:** 1.0.0  
**Status:** CONFIRMED & PROPOSED API Baseline  
**Authority Sources:** [SRS.md](../SRS.md) §3.1, §3.12, §4, §10; [PRD.md](../PRD.md) §15, §16  

---

## 1. API Architecture & General Principles

- **Protocol & Serialization:** HTTP/1.1 (HTTPS in production), JSON payloads and responses (`Content-Type: application/json`).
- **Base Route:** `/api`
- **Authentication:** All protected endpoints require an `Authorization: Bearer <JWT>` header containing a valid Supabase Auth token. Unauthenticated requests receive HTTP 401.
- **Identity Derivation:** The backend derives the authenticated `user_id` strictly from the decoded JWT claims (`sub`). The API rejects request-body or query parameter user IDs.
- **Standard Error Envelope:**
  Every error returned by the API adheres to the standard error structure:
  ```json
  {
    "error": {
      "code": "ERROR_CODE_STRING",
      "message": "User-facing safe explanation of the error.",
      "details": {
        "field": "optional_field_name",
        "reason": "optional_granular_reason"
      },
      "request_id": "c8a417df-3801-4475-8025-a4e98f79ce55"
    }
  }
  ```

---

## 2. HTTP Status Code Conventions

| HTTP Status | Meaning | Typical Usage in System |
|---|---|---|
| **200 OK** | Success | Successful resource retrieval, update, or recommendation results (including empty `[]`). |
| **201 Created** | Created | Successful record insertion (e.g. workout completion logged). |
| **400 Bad Request** | Malformed Syntax | Malformed JSON body or invalid HTTP headers. |
| **401 Unauthorized** | Authentication Failed | Missing, malformed, or expired Supabase JWT token. |
| **403 Forbidden** | Authorization Failed | Valid token, but user lacks permissions (e.g. attempting to read another user's private data). |
| **404 Not Found** | Resource Missing | Workout session or historical record does not exist. |
| **409 Conflict** | State Conflict | **Safety hold active** (`SAFETY_HOLD_ACTIVE`), or duplicate completion submission. |
| **422 Unprocessable** | Validation Failure | Valid JSON syntax but invalid field values (e.g. duration out of 5–180 range, invalid goal string). |
| **500 Server Error** | Unexpected Failure | Uncaught exception; returns safe generic message and server logs request ID. |
| **503 Unavailable** | Dependency Down | Supabase PostgreSQL or Auth service is unreachable. |

---

## 3. Endpoint Inventory & Request/Response Contracts

### 3.1 Health Check
- **Route:** `GET /api/health`
- **Auth:** Public
- **Description:** Verifies service uptime and database connectivity without exposing sensitive credentials.
- **Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-10-28T20:30:00Z",
    "version": "1.0.0"
  }
  ```

---

### 3.2 User Profile Management

#### `GET /api/profile`
- **Auth:** Required (Bearer JWT)
- **Description:** Retrieves the authenticated user's profile and safety status.
- **Response (200 OK):**
  ```json
  {
    "user_id": "4b684cb3-00e9-4e0e-9eb2-0fbc35848bb4",
    "primary_goal": "Muscle gain",
    "fitness_level": "Intermediate",
    "equipment": ["Dumbbells", "Bench", "Resistance bands"],
    "available_duration_minutes": 45,
    "safety_hold": false,
    "safety_screening_status": "CLEARED",
    "safety_confirmed_at": "2026-10-28T10:00:00Z",
    "updated_at": "2026-10-28T10:00:00Z"
  }
  ```
- **Response (404 Not Found):** If user has signed up but not yet saved a profile.

#### `PUT /api/profile`
- **Auth:** Required (Bearer JWT)
- **Description:** Creates or updates the user profile and physical safety screening.
- **Request Body:**
  ```json
  {
    "primary_goal": "Muscle gain",
    "fitness_level": "Intermediate",
    "equipment": ["Dumbbells", "Bench", "Resistance bands"],
    "available_duration_minutes": 45,
    "screening_answers": {
      "has_active_injury": false,
      "has_ongoing_limitation": false,
      "has_current_pain": false,
      "has_urgent_symptoms": false
    },
    "confirm_cleared": true
  }
  ```
- **Validation Rules:**
  - `primary_goal`: Must match one of 6 controlled goals.
  - `fitness_level`: Must be `Beginner`, `Intermediate`, or `Advanced`.
  - `equipment`: Must be a non-empty array of items from the 10 controlled equipment list.
  - `available_duration_minutes`: Integer between 5 and 180.
  - If any screening flag (`has_active_injury`, `has_ongoing_limitation`, `has_current_pain`) is `true`, `safety_hold` is set to `true` and `safety_screening_status` set to `'HOLD'`.
  - If `has_urgent_symptoms` is `true`, `safety_screening_status` is set to `'URGENT_SYMPTOMS'`.
- **Response (200 OK):** Returns the updated profile object.
- **Error (422 Unprocessable):** If mandatory fields are missing or values are out of range.

---

### 3.3 Workout Recommendations

#### `POST /api/recommendations`
- **Auth:** Required (Bearer JWT)
- **Description:** Evaluates eligibility and generates up to 5 personalized recommendations.
- **Request Body:**
  ```json
  {}
  ```
  *(Request uses stored user profile as source of truth. Optional ephemeral override attributes are permissible if validated, but safety state cannot be overridden).*
- **Execution Logic:**
  1. Load profile for token `user_id`.
  2. If `safety_hold == true` or `safety_screening_status != 'CLEARED'`, reject with HTTP 409.
  3. Load approved sessions from catalogue.
  4. Apply hard filters (difficulty, equipment, verified duration).
  5. If 0 eligible candidates, return HTTP 200 with empty list.
  6. Calculate Cosine Similarity over feature vectors.
  7. Rank candidates (Primary Goal match > Cosine Similarity > Tie-break ID).
  8. Return top 5 items with match explanations and duration warnings.
- **Response (200 OK — Candidates Found):**
  ```json
  {
    "results": [
      {
        "workout_id": "session-upper-body-blast",
        "name": "Upper Body Hypertrophy Blast",
        "primary_goal": "Muscle gain",
        "difficulty": "Intermediate",
        "duration_minutes": 45,
        "required_equipment": ["Dumbbells", "Bench"],
        "workout_type": "Strength",
        "instructions": "Warm up with dynamic arm circles, then proceed through exercises.",
        "similarity_score": 0.942,
        "duration_caution": null,
        "match_explanations": [
          "Directly aligns with your primary goal of Muscle gain.",
          "Difficulty level 'Intermediate' matches your current experience.",
          "All required equipment (Dumbbells, Bench) is in your available set.",
          "Estimated duration (45 mins) fits your available workout time."
        ],
        "exercises": [
          {
            "sequence_number": 1,
            "exercise_id": "dumbbell-bench-press",
            "name": "Dumbbell Bench Press",
            "sets": 4,
            "reps": "8-12",
            "duration_seconds": null,
            "rest_seconds": 90,
            "instructions": "Lie flat on bench, press dumbbells up smoothly."
          }
        ]
      }
    ],
    "message": "Successfully generated 1 personalized recommendation."
  }
  ```
- **Response (200 OK — Empty Results):**
  ```json
  {
    "results": [],
    "message": "No workout sessions currently match your equipment set and level. Try selecting additional equipment."
  }
  ```
- **Response (409 Conflict — Safety Hold Active):**
  ```json
  {
    "error": {
      "code": "SAFETY_HOLD_ACTIVE",
      "message": "Personalized recommendations are paused due to an active safety hold or physical limitation.",
      "details": {
        "status": "HOLD",
        "action_required": "Please resolve safety screening or consult a medical professional before resuming."
      },
      "request_id": "e45f91e8-7822-4467-bba2-5bb9168fa554"
    }
  }
  ```

---

### 3.4 Workout History & Completion

#### `POST /api/history`
- **Auth:** Required (Bearer JWT)
- **Description:** Explicitly marks a workout session as completed.
- **Request Body:**
  ```json
  {
    "workout_id": "session-upper-body-blast",
    "completed_at": "2026-10-28T20:15:00Z",
    "idempotency_key": "7b8e19e0-6a98-44d4-9d55-6b45f1b1c28b"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "id": "f51f4967-33a7-4b7f-a63e-f63bda4954ea",
    "workout_id": "session-upper-body-blast",
    "completed_at": "2026-10-28T20:15:00Z",
    "session_name": "Upper Body Hypertrophy Blast",
    "primary_goal": "Muscle gain"
  }
  ```
- **Error (409 Conflict):** If duplicate completion submission occurs without idempotency resolution.

#### `GET /api/history`
- **Auth:** Required (Bearer JWT)
- **Description:** Returns the authenticated user's completion history, ordered newest first (`completed_at DESC`).
- **Response (200 OK):**
  ```json
  {
    "history": [
      {
        "id": "f51f4967-33a7-4b7f-a63e-f63bda4954ea",
        "workout_id": "session-upper-body-blast",
        "session_name": "Upper Body Hypertrophy Blast",
        "primary_goal": "Muscle gain",
        "completed_at": "2026-10-28T20:15:00Z"
      }
    ],
    "total_count": 1
  }
  ```

---

### 3.5 Extended Dashboard Metrics

#### `GET /api/dashboard`
- **Auth:** Required (Bearer JWT)
- **Description:** Provides aggregated metrics based on explicit completions.
- **Response (200 OK):**
  ```json
  {
    "total_completed": 12,
    "recent_activity": [
      {
        "workout_id": "session-upper-body-blast",
        "session_name": "Upper Body Hypertrophy Blast",
        "completed_at": "2026-10-28T20:15:00Z"
      }
    ],
    "weekly_trends": [
      {"week_start": "2026-10-12", "completion_count": 3},
      {"week_start": "2026-10-19", "completion_count": 5},
      {"week_start": "2026-10-26", "completion_count": 4}
    ],
    "goal_wise_counts": {
      "Muscle gain": 8,
      "Fat loss": 2,
      "General fitness": 2,
      "Endurance": 0,
      "Strength improvement": 0,
      "Flexibility and mobility": 0
    }
  }
  ```

---

### 3.6 Account Deletion

#### `DELETE /api/account`
- **Auth:** Required (Bearer JWT)
- **Description:** Permanently deletes the authenticated user's Supabase Auth identity, private profile, and workout history.
- **Request Body:**
  ```json
  {
    "confirmation": "DELETE_MY_ACCOUNT"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Account and associated private data have been permanently deleted."
  }
  ```
- **Error (400 Bad Request):** If confirmation string is omitted or invalid.

---

### 3.7 General Nutrition Guidance (Optional)

#### `GET /api/nutrition`
- **Auth:** Public or Required
- **Description:** Returns general, non-medical nutrition educational content.
- **Response (200 OK):**
  ```json
  {
    "disclaimer": "This guidance is for general educational purposes only and is not medical advice.",
    "topics": [
      {"id": "macronutrients", "title": "Balanced Macronutrients", "summary": "Understanding whole food proteins, complex carbs, and essential fats."},
      {"id": "hydration", "title": "Hydration Guidelines", "summary": "Recommended daily fluid intake and electrolyte balance during activity."}
    ]
  }
  ```
