# TESTING.md — Verification Strategy & Acceptance Test Specification

**Project:** Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning  
**Version:** 1.0.0  
**Status:** CONFIRMED & PROPOSED Test Specifications  
**Authority Sources:** [SRS.md](../SRS.md) §9, §14; [PRD.md](../PRD.md) §17, §18  

---

## 1. Testing Objectives & Quality Gates

The testing strategy guarantees that:
1. **Zero Hard-Constraint Violations:** Hard eligibility filters (difficulty, equipment, duration, safety hold) are strictly unyielding.
2. **Reproducibility:** Given identical inputs and catalogue version, recommendation ordering is 100% deterministic.
3. **Security & Privacy Isolation:** Row Level Security (RLS) and token checks prevent cross-user data tampering.
4. **Academic Benchmark Validity:** The Cosine Similarity model is quantitatively evaluated against a heuristic baseline using NDCG@5 across $\ge 10$ synthetic user profiles.
5. **Quality Gate for Release:** All 26 Mandatory Acceptance Tests (`AT-01` to `AT-26`) must pass with 100% success before any code release.

---

## 2. Mandatory Acceptance Test Suite (AT-01 to AT-26)

| Test ID | Category | Requirement | Test Verification Condition | Target |
|---|---|---|---|---|
| **AT-01** | Eligibility | `REC-05` | Beginner user never receives Intermediate or Advanced sessions. | PASS |
| **AT-02** | Eligibility | `REC-05` | Intermediate user receives Beginner and Intermediate sessions, never Advanced. | PASS |
| **AT-03** | Eligibility | `REC-05` | Advanced user may receive Beginner, Intermediate, and Advanced sessions. | PASS |
| **AT-04** | Equipment | `EQ-02`, `EQ-04` | Session requiring unavailable equipment is excluded unless approved alternative satisfies it. | PASS |
| **AT-05** | Equipment | `PROF-07` | Empty equipment selection is rejected; blocks recommendation generation. | PASS |
| **AT-06** | Data Quality | `DATA-09` | Missing or unverified session duration excludes the session from candidates. | PASS |
| **AT-07** | Data Quality | `DATA-06`, `07` | Unapproved (`quarantined`) records are never recommended. | PASS |
| **AT-08** | Safety Hold | `SAFE-02`, `05` | Active safety hold blocks recommendation generation before ranking (returns HTTP 409). | PASS |
| **AT-09** | Safety Hold | `SAFE-06` | Changing goal, equipment, or duration does not bypass an active safety hold. | PASS |
| **AT-10** | Urgent Care | `SAFE-04` | Urgent symptoms block recommendations and present emergency care guidance. | PASS |
| **AT-11** | Results Count | `REC-14` | Fewer than 5 eligible sessions returns all qualifying sessions without relaxing filters. | PASS |
| **AT-12** | Results Count | `REC-15` | Zero eligible sessions returns HTTP 200 with empty list `[]` and explanatory message. | PASS |
| **AT-13** | Results Count | `REC-13` | No response ever contains more than 5 sessions. | PASS |
| **AT-14** | Determinism | `REC-18` | Repeated identical requests against identical data/config yield identical ordered results. | PASS |
| **AT-15** | ML Robustness | `REC-11` | Zero-vector or undefined cosine similarity handles gracefully without NaN/Infinity or crash. | PASS |
| **AT-16** | Explanations | `REC-16` | Match explanations cite verified profile and session attributes only. | PASS |
| **AT-17** | Authorization | `AUTH-08` | Authenticated User A cannot read or modify User B's profile, history, or dashboard. | PASS |
| **AT-18** | Authentication | `AUTH-06` | Expired, forged, or missing JWT tokens return HTTP 401 Unauthorized. | PASS |
| **AT-19** | History | `HIST-02` | Completion record is created only after explicit completion action. | PASS |
| **AT-20** | Deduplication | `HIST-04` | Duplicate completion submissions are prevented via idempotency or conflict rejection. | PASS |
| **AT-21** | Analytics | `DASH-01`–`04` | Dashboard totals, weekly trends, and goal-wise counts accurately reflect history rows. | PASS |
| **AT-22** | Deletion | `DEL-03`, `04` | Account deletion removes Auth user and private data while preserving shared catalogue. | PASS |
| **AT-23** | Nutrition | `NUT-05`, `06` | Nutrition content contains no calorie calculations, personalized meal plans, or medical claims. | PASS |
| **AT-24** | Resilience | `API-06` | Malformed JSON and database timeouts return controlled JSON error envelopes. | PASS |
| **AT-25** | Network Security| `API-08` | CORS accepts configured frontend origin (`localhost:5173`) and rejects unapproved origins. | PASS |
| **AT-26** | Release Gate | PRD §21 | All defined acceptance tests pass before release. | PASS |

---

## 3. Machine Learning & Ranking Evaluation Specification

### 3.1 Evaluation Objectives
Compare the **Content-Based Cosine Similarity Ranker** against the **Deterministic Baseline Ranker** (which applies the same hard filters, followed by sorting by primary goal, secondary goal, and `workout_id`).

### 3.2 Metric: Normalized Discounted Cumulative Gain at 5 (NDCG@5)
$$DCG@5 = \sum_{i=1}^{5} \frac{2^{rel_i} - 1}{\log_2(i + 1)}$$
$$NDCG@5 = \frac{DCG@5}{IDCG@5}$$
Where $rel_i \in \{0, 1, 2, 3\}$ represents human relevance labels:
- **0:** Not relevant
- **1:** Slightly relevant
- **2:** Relevant
- **3:** Highly relevant

### 3.3 Synthetic Test Profiles (Minimum 10)

```json
[
  {"id": "PROF-01", "name": "Beginner Bodyweight Muscle", "goal": "Muscle gain", "level": "Beginner", "equip": ["Bodyweight only"], "duration": 30, "hold": false},
  {"id": "PROF-02", "name": "Intermediate Dumbbell Strength", "goal": "Strength improvement", "level": "Intermediate", "equip": ["Dumbbells", "Bench"], "duration": 45, "hold": false},
  {"id": "PROF-03", "name": "Advanced Full Gym Endurance", "goal": "Endurance", "level": "Advanced", "equip": ["Barbell", "Bench", "Gym machines", "Cable machine"], "duration": 60, "hold": false},
  {"id": "PROF-04", "name": "Active Injury Hold", "goal": "Fat loss", "level": "Intermediate", "equip": ["Dumbbells"], "duration": 30, "hold": true},
  {"id": "PROF-05", "name": "Beginner Mobility & Recovery", "goal": "Flexibility and mobility", "level": "Beginner", "equip": ["Foam roller", "Bodyweight only"], "duration": 20, "hold": false},
  {"id": "PROF-06", "name": "Kettlebell Fat Loss", "goal": "Fat loss", "level": "Intermediate", "equip": ["Kettlebells"], "duration": 40, "hold": false},
  {"id": "PROF-07", "name": "Zero Compatible Equipment Edge", "goal": "Strength improvement", "level": "Intermediate", "equip": ["Exercise ball"], "duration": 45, "hold": false},
  {"id": "PROF-08", "name": "Short Duration Crunch", "goal": "General fitness", "level": "Beginner", "equip": ["Bodyweight only"], "duration": 15, "hold": false},
  {"id": "PROF-09", "name": "Advanced Calisthenics", "goal": "Muscle gain", "level": "Advanced", "equip": ["Bodyweight only"], "duration": 60, "hold": false},
  {"id": "PROF-10", "name": "Resistance Band General", "goal": "General fitness", "level": "Intermediate", "equip": ["Resistance bands"], "duration": 35, "hold": false}
]
```

### 3.4 Evaluation Execution Command
Provide reviewer-assigned labels for the current workout IDs in a JSON file, then run:

```bash
python scripts/evaluate_ranking.py --labels path/to/reviewer_relevance_labels.json
```
- The script outputs NDCG@5 for Cosine vs Baseline and generates `evaluation_report.md`.

---

## 4. Performance & Latency Testing

- **Target:** **p95 recommendation pipeline latency < 1.0 second** on local development environment (`NFR-PERF-01`).
- **Benchmark Script:** `tests/benchmark_latency.py`
  - Sends 100 recommendation requests across diverse profiles.
  - Measures backend processing duration (excluding external internet roundtrips).
  - Computes p50, p90, and p95 latency percentiles.

---

## 5. Test Execution Instructions

The backend unit suite runs without a Supabase account. Auth/database integration tests are skipped by default and must only run against a disposable Supabase project. Before enabling them, configure `backend/.env` with that project's Auth URL and keys, then set `RUN_SUPABASE_INTEGRATION=1`, `TEST_SUPABASE_PROJECT_REF=<project-ref>`, and `TEST_DATABASE_URL=<test-project-postgres-uri>`. The test fixture creates temporary Auth users and fixture sessions, then deletes them during teardown.

### 5.1 Backend Unit & Integration Tests (pytest)
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

### 5.2 Frontend Component & Integration Tests (Vitest)
```bash
cd frontend
npm test
```
