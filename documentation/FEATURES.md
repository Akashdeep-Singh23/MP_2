# FEATURES.md — Authoritative Feature Inventory & Behavioral Specification

**Project:** Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning  
**Version:** 1.0.0  
**Status:** CONFIRMED & PROPOSED Feature Specifications  
**Authority Sources:** [PRD.md](../PRD.md) §6, §8–§16; [SRS.md](../SRS.md) §3.1–§3.12  

---

## 1. Feature Traceability & Priority Summary

| Feature ID | Feature Name | Priority | Core SRS Mapping | Status |
|---|---|---|---|---|
| **FEAT-01** | User Authentication & Session Management | P0 (MVP) | `AUTH-01` to `AUTH-08` | Documented / Ready |
| **FEAT-02** | Mandatory Profile & Preference Management | P0 (MVP) | `PROF-01` to `PROF-13` | Documented / Ready |
| **FEAT-03** | Mandatory Physical Safety Screening & Hold | P0 (MVP) | `SAFE-01` to `SAFE-12` | Documented / Ready |
| **FEAT-04** | Catalogue Ingestion, Validation & Curation | P0 (MVP) | `DATA-01` to `DATA-14` | Documented / Ready |
| **FEAT-05** | Equipment Compatibility & Substitution | P0 (MVP) | `EQ-01` to `EQ-07` | Documented / Ready |
| **FEAT-06** | Hard-Filtered Cosine Similarity Recommender | P0 (MVP) | `REC-01` to `REC-20` | Documented / Ready |
| **FEAT-07** | Transparent Match Explanations & Cautions | P0 (MVP) | `REC-16`, `REC-17` | Documented / Ready |
| **FEAT-08** | Workout Session Detail & Execution View | P0 (MVP) | `SESSION-01` to `03` | Documented / Ready |
| **FEAT-09** | Explicit Workout Completion & History | P0 (MVP) | `HIST-01` to `HIST-08` | Documented / Ready |
| **FEAT-10** | Extended Progress Analytics Dashboard | P0 (MVP) | `DASH-01` to `DASH-07` | Documented / Ready |
| **FEAT-11** | General Educational Nutrition Guidance | P1 (MVP) | `NUT-01` to `NUT-07` | Documented / Ready |
| **FEAT-12** | Authenticated Account & Private Data Deletion | P0 (MVP) | `DEL-01` to `DEL-07` | Documented / Ready |
| **FEAT-13** | ML Evaluation Benchmark (NDCG@5 vs Baseline) | P0 (MVP) | `EV-01` to `EV-09` | Documented / Ready |
| **FEAT-14** | Public Landing Page & Hero Section Experience | P0 (MVP) | SRS §2.2, §4.1; PRD §6 | Documented / Ready |

---

## 2. Detailed Feature Specifications

### FEAT-01: User Authentication & Session Management
- **Description:** Allows users to register with email/password, sign in, maintain session persistence via JWT, and securely sign out.
- **User Value:** Ensures workout history and health screening status remain private to the user.
- **Preconditions:** Valid internet connectivity to reach hosted Supabase Auth.
- **Inputs:** Email, Password.
- **Outputs:** JWT Access Token, User Session object.
- **Business Rules:**
  - Email verification is optional for the MVP (`AUTH-04`); registration grants immediate application access.
  - Backend must validate bearer JWT on every protected endpoint (`AUTH-05`).
  - Backend derives `user_id` strictly from token claims (`AUTH-07`).
- **Acceptance Criteria:** `AT-17`, `AT-18`.

---

### FEAT-02: Mandatory Profile & Preference Management
- **Description:** Users configure and update their primary fitness goal, fitness level, available equipment, and available workout duration.
- **User Value:** Establishes the exact parameters used to filter and score workout sessions.
- **Inputs:**
  - `primary_goal`: Exactly one of the 6 supported goals.
  - `fitness_level`: `Beginner`, `Intermediate`, or `Advanced`.
  - `equipment`: Non-empty array of items selected from the 10 controlled equipment items.
  - `available_duration_minutes`: Integer between 5 and 180.
- **Outputs:** Persisted profile record in `profiles` table.
- **Business Rules:**
  - Empty equipment array is strictly rejected (`PROF-07`); bodyweight-only must be explicitly selected.
  - Duration outside 5–180 minutes is rejected with HTTP 422 (`PROF-05`).
  - No optional fields (e.g. weight, height) are required for MVP (`PROF-11`).
- **Acceptance Criteria:** `AT-05`.

---

### FEAT-03: Mandatory Physical Safety Screening & Backend Hold
- **Description:** Pre-recommendation screening for active injuries, ongoing limitations, unexplained pain, and urgent cardiovascular symptoms.
- **User Value:** Protects users from performing unsuitable exercises that could exacerbate physical injuries.
- **Inputs:** Responses to screening questions (injury, pain, limitations, urgent symptoms).
- **Outputs:** `safety_hold` flag (`true`/`false`), `safety_screening_status` (`CLEARED`, `HOLD`, `URGENT_SYMPTOMS`).
- **Business Rules:**
  - Any active injury, pain, or limitation sets `safety_hold = true` (`SAFE-02`, `SAFE-03`).
  - Recommendation requests while hold is active return HTTP 409 `SAFETY_HOLD_ACTIVE` (`SAFE-05`).
  - Changing goals or equipment cannot bypass a hold (`SAFE-06`).
  - Resumption requires explicit user confirmation that the condition is resolved (`SAFE-08`).
  - Urgent symptoms display emergency care advice (`SAFE-04`).
- **Acceptance Criteria:** `AT-08`, `AT-09`, `AT-10`.

---

### FEAT-04: Catalogue Ingestion, Validation & Curation
- **Description:** Data pipeline importing Free Exercise DB JSON, enforcing schema validation, quarantining invalid records, and approving curated sessions.
- **User Value:** Guarantees that only structurally sound, reviewed workout sessions are recommended.
- **Target:** ~30 approved sessions with $\ge 5$ sessions per primary goal.
- **Business Rules:**
  - Every session must have unique `workout_id`, name, primary goal, difficulty, duration, equipment, exercise sequence, and sets/reps/duration/rest (`DATA-01`, `DATA-02`).
  - Missing duration or equipment quarantines the record (`DATA-04`, `DATA-07`).
- **Acceptance Criteria:** `AT-06`, `AT-07`.

---

### FEAT-05: Equipment Compatibility & Substitution
- **Description:** Determines session eligibility based on whether 100% of required equipment is available to the user or covered by an approved alternative.
- **Business Rules:**
  - Complete subset check: `session.required_equipment` $\subseteq$ `user.equipment` (`EQ-02`).
  - If a required item is missing, check `exercise_alternatives` for an approved substitution (`EQ-04`).
  - Missing equipment cannot be inferred as bodyweight-compatible (`EQ-03`).
- **Acceptance Criteria:** `AT-04`.

---

### FEAT-06: Hard-Filtered Cosine Similarity Recommender
- **Description:** Recommends up to 5 workout sessions using strict eligibility filters followed by Cosine Similarity ranking over feature vectors.
- **Pipeline:**
  1. Verify safety hold is clear.
  2. Hard filters: Difficulty mapping (`Beginner` $\to$ `Beginner`; `Intermediate` $\to$ `Beginner`+`Intermediate`; `Advanced` $\to$ all 3), Equipment availability, Verified duration.
  3. Feature vector construction (goal, category, target muscles, normalized duration fit).
  4. Cosine Similarity calculation with zero-vector safeguard (`norm(v) == 0`).
  5. Primary goal match tiering (primary matches strictly ahead of secondary matches).
  6. Deterministic tie-break by `workout_id`.
  7. Truncate to top 5 results; return HTTP 200 with `[]` if none qualify.
- **Business Rules:** Hard filters are *never* relaxed to fill the list (`REC-14`).
- **Acceptance Criteria:** `AT-01` to `AT-03`, `AT-11` to `AT-15`.

---

### FEAT-07: Transparent Match Explanations & Cautions
- **Description:** Provides plain-language explanations of why each session was recommended and displays duration warnings when appropriate.
- **Business Rules:**
  - Explanations must cite verified data only (`REC-16`).
  - If session duration exceeds user's available time by $>10$ minutes, a clear warning badge is attached (`REC-10`).
- **Acceptance Criteria:** `AT-16`.

---

### FEAT-08: Workout Session Detail & Execution View
- **Description:** Full breakdown of a workout session, including ordered exercises, sets, reps, duration, instructions, and interactive rest timers.
- **User Value:** Gives users actionable step-by-step guidance to execute the session.
- **Acceptance Criteria:** `SESSION-01` to `SESSION-03`.

---

### FEAT-09: Explicit Workout Completion & History
- **Description:** Records completed workouts when the user explicitly clicks "Mark Complete", storing a static snapshot of session metadata.
- **Business Rules:**
  - Recorded only on explicit user action (`HIST-02`).
  - Duplicate prevention via client idempotency key or 60-second cooldown window (`HIST-04`).
  - Returns history ordered newest first (`HIST-08`).
- **Acceptance Criteria:** `AT-19`, `AT-20`.

---

### FEAT-10: Extended Progress Analytics Dashboard
- **Description:** Visual analytics displaying total completed sessions, recent activity, weekly completion trends, and goal-wise completion counts.
- **Business Rules:**
  - Metrics derived strictly from explicit completion records, not views (`DASH-06`).
  - Shows clear empty state when user has 0 completions (`DASH-05`).
- **Acceptance Criteria:** `AT-21`.

---

### FEAT-11: General Educational Nutrition Guidance
- **Description:** Optional, non-medical educational content covering macronutrients, hydration, and healthy eating habits.
- **Business Rules:**
  - Prohibited: Calorie deficit/surplus calculators, personalized meal plans, macro targets, BMI, supplements, therapeutic diets (`NUT-05`, `NUT-06`).
  - Optional viewing; skipping does not block workout recommendations (`NUT-01`).
- **Acceptance Criteria:** `AT-23`.

---

### FEAT-12: Authenticated Account & Private Data Deletion
- **Description:** Allows users to permanently delete their account and private data (profile and history) with explicit confirmation.
- **Business Rules:**
  - Requires explicit confirmation string (`"DELETE_MY_ACCOUNT"`) (`DEL-02`).
  - Calls the deployed JWT-protected `delete-account` Edge Function; auth deletion cascades to `profiles` and `workout_history` (`DEL-03`).
  - Shared catalogue (`exercises`, `workout_sessions`) remains untouched (`DEL-04`).
- **Acceptance Criteria:** `AT-22`.

---

### FEAT-13: ML Evaluation Benchmark (NDCG@5 vs Baseline)
- **Description:** Evaluation harness comparing Cosine Similarity ranker against a heuristic baseline across $\ge 10$ synthetic user profiles.
- **Business Rules:**
  - Evaluated on identical candidates and 0–3 human relevance labels (`EV-06`, `EV-07`).
  - Measures p50 and p95 pipeline latency targeting $<1.0$s (`EV-08`).
- **Acceptance Criteria:** Acceptance metrics in PRD §18.

---

### FEAT-14: Public Landing Page & Hero Section Experience
- **Description:** An unauthenticated, public-facing landing page featuring a prominent Hero Section, a factual recommendation-process overview, 4-pillar value propositions, 3-step pipeline walkthrough, 6 supported fitness goals showcase, and academic attribution.
- **User Value:** Contextualizes the safety-first philosophy, explainable AI model, and equipment-matching capabilities of the system before requesting user registration.
- **Preconditions:** Accessible by unauthenticated visitors without a bearer token.
- **Inputs:** User clicks on navigation links ("Sign In", "Get Started Free", "Explore Scientific Approach", or Goal showcase pills).
- **Outputs:** Responsive visual landing page, smooth navigation transitions to authentication routes (`/signup`, `/login`), and informative educational content.
- **Business Rules:**
  - Accessible to public visitors without requiring authentication (SRS §2.2).
  - Contains mandatory non-medical disclaimers framing the application as a fitness-information tool rather than clinical diagnostic software.
  - Hero content describes recommendation stages without presenting a fabricated workout or score.
  - Direct call-to-action routing seamlessly into the profile onboarding flow.
- **Acceptance Criteria:** Wireframe and interaction criteria defined in `DESIGN.md` §3.1.
