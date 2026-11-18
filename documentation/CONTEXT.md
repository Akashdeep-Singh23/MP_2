# CONTEXT.md — Project Knowledge Base, Decisions, and Uncertainty Record

**Project:** Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning  
**Version:** 1.0.0  
**Status:** Baseline Established  
**Last Updated:** 2026-10-28  
**Author:** Technical Documentation Architect  

---

## 1. Project Understanding & Executive Summary

The project is an academic B.Tech AIML capstone application providing transparent, safety-first, personalized workout recommendations.
Unlike commercial fitness applications that promote unverified exercise collections, black-box AI chatbots, or uncurated workouts, this system adheres to strict engineering constraints:
1. **Unit of Recommendation:** Complete, reviewed workout sessions (ordered sequence of exercises, prescribed sets/reps/duration, explicit rest intervals) rather than disconnected individual exercises.
2. **Safety First:** Mandatory pre-recommendation physical screening. Any active injury, physical limitation, current/unexplained pain, or urgent symptoms (chest pain, shortness of breath, fainting) triggers an immediate **Safety Hold** (`SAFETY_HOLD_ACTIVE`, HTTP 409). Safety holds are enforced strictly in the FastAPI backend on every recommendation request, cannot be bypassed through preference changes or frontend manipulation, and require deliberate user resolution confirmation (not medical clearance).
3. **Deterministic Filtering Before Ranking:** Content-based Cosine Similarity ranking runs *only* on the candidate set that survives strict hard eligibility filters (safety hold clear, session approved, difficulty permitted for user level, 100% equipment availability or verified alternative, verified duration, non-corrupted data). Hard filters are *never* relaxed.
4. **Transparent & Deterministic Recommendations:** Up to 5 sessions returned, with evidence-based explanations citing exact profile-session matches (goal, difficulty, equipment, duration fit). Same inputs + same catalogue version = identical ordered output.
5. **Evaluation Against Baseline:** The Cosine Similarity ranker is evaluated against a deterministic heuristic baseline on >=10 synthetic profiles using NDCG@5 (0–3 human relevance labels) and p95 pipeline latency target (<1s on local development setup).
6. **Architecture Model:** Local React + Vite client, local Python FastAPI backend, hosted Supabase Auth (JWT) and Supabase PostgreSQL with Row Level Security (RLS).

---

## 2. Confirmed Requirements and Constraints

| ID | Status | Category | Description | Authority Source |
|---|---|---|---|---|
| **REQ-CONF-01** | CONFIRMED | Architecture | Local demonstration with React/Vite (frontend) and FastAPI (backend); Supabase Auth & PostgreSQL are hosted cloud services. | PRD §2, §15; SRS §2.1, §12.1 |
| **REQ-CONF-02** | CONFIRMED | Recommendation Unit | System recommends complete workout sessions containing ordered exercises, prescribed sets/reps or duration, and rest intervals. | PRD §10.1; SRS §3.6 (REC-01) |
| **REQ-CONF-03** | CONFIRMED | Supported Goals | Exactly six primary goals supported: (1) Muscle gain, (2) Fat loss, (3) Endurance, (4) General fitness, (5) Strength improvement, (6) Flexibility and mobility. | PRD §7; SRS §3.2 (PROF-03) |
| **REQ-CONF-04** | CONFIRMED | Fitness Levels | Exactly three levels: Beginner, Intermediate, Advanced. Mapping: Beginner → Beginner only; Intermediate → Beginner + Intermediate; Advanced → all three. | PRD §10.4; SRS §3.6 (REC-05) |
| **REQ-CONF-05** | CONFIRMED | Controlled Equipment | Exactly ten items: Bodyweight only, Dumbbells, Resistance bands, Barbell, Bench, Gym machines, Kettlebells, Cable machine, Exercise ball, Foam roller. Empty selection is prohibited. | PRD §8.4; SRS §3.2 (PROF-06, PROF-07) |
| **REQ-CONF-06** | CONFIRMED | Duration Limits | Validated range: 5 to 180 minutes. Soft preference; exceeding available duration displays warning. | PRD §8.3; SRS §3.2 (PROF-05), §3.6 (REC-10) |
| **REQ-CONF-07** | CONFIRMED | Safety Enforcement | Backend enforces screening/hold. Active hold returns HTTP 409 `SAFETY_HOLD_ACTIVE`. No bypass allowed. | PRD §9; SRS §3.3 (SAFE-01 to SAFE-12) |
| **REQ-CONF-08** | CONFIRMED | ML Ranking Pipeline | Hard filters first → Content-based Cosine Similarity on feature vectors → Primary goal match tiering → Deterministic workout_id tie-break. Maximum 5 results. | PRD §10.5, §10.6; SRS §3.6 (REC-01 to REC-19) |
| **REQ-CONF-09** | CONFIRMED | Source Dataset | Free Exercise DB (JSON). Curate ~30 complete sessions, >=5 per primary goal. | PRD §11; SRS §3.4 (DATA-01 to DATA-14) |
| **REQ-CONF-10** | CONFIRMED | History & Dashboard | Explicit completion action only. Metrics: Total completed, recent activity, weekly trends (by completion timestamp), goal-wise counts. Duplicate completion prevention required. | PRD §12; SRS §3.8, §3.9 |
| **REQ-CONF-11** | CONFIRMED | Nutrition Guidance | Optional, general non-medical education only. Prohibited: calorie calculation, deficit/surplus, macros, BMI, meal plans, therapeutic diets, supplement dosages. | PRD §13; SRS §3.10 |
| **REQ-CONF-12** | CONFIRMED | Auth & Privacy | Direct React → Supabase Auth. FastAPI validates JWT bearer token on protected endpoints. User ID derived from token. RLS on private tables. Deliberate account deletion deletes auth identity + private data. | PRD §14; SRS §3.1, §3.11, §7.2, §7.3 |
| **REQ-CONF-13** | CONFIRMED | Autonomous Agents | No autonomous AI agents in MVP. Agent tools and agent orchestration are NOT APPLICABLE. | PRD §5, §19; SRS §1.2 |
| **REQ-CONF-14** | CONFIRMED | MCP Servers | No Model Context Protocol servers required for MVP. MCP is NOT APPLICABLE. | PRD §5, §19; SRS §1.2 |
| **REQ-CONF-15** | CONFIRMED | Public Landing & Hero | Public landing page with Hero section, factual recommendation-process overview, 4-pillar value propositions, 3-step pipeline walkthrough, and non-medical disclaimer. | Explicit User Instruction; SRS §2.2, §4.1; PRD §6 |

---

## 3. Source Conflicts and Contradictions

During the reconciliation of SRS.md and PRD.md, the following checks were performed:
- **Scope & Goals:** Both documents align on the 6 goals, 3 levels, 10 equipment items, 5–180 minute duration, and ~30 session dataset target.
- **Safety Enforcement:** Both documents specify backend hold enforcement, HTTP 409 status, and non-bypassability.
- **Account Deletion:** Both documents require deliberate confirmation, trusted backend execution, deletion of auth identity + private data, and preservation of the shared exercise/session catalogue.
- **Baseline Comparison:** Both documents agree on evaluating Cosine Similarity vs a deterministic primary-goal/secondary-goal baseline using NDCG@5 on >=10 synthetic profiles.

**Result:** No unresolvable direct contradictions exist between SRS and PRD. Both documents are mature v1.0 specifications designed in harmony. Minor implementation ambiguities are recorded below as open questions.

---

## 4. Unanswered Questions & Clarification Log

### Q-001: Exact Cosine Similarity Feature Vector Representation
- **Status:** PROPOSED (Awaiting User Approval / Development Audit)
- **Priority:** High
- **Source:** SRS §6.1, §6.3; PRD §10.5, §22
- **Question:** How should profile and session attributes be encoded into feature vectors for Cosine Similarity?
- **Reason:** SRS §6.1 specifies content-based Cosine Similarity over documented feature vectors, but delegates exact encoding dimensions and soft-weights to implementation design.
- **Affected documents:** ARCHITECTURE.md, API.md, TESTING.md, FEATURES.md
- **Proposed Solution:** 
  Construct a normalized fixed-length vector across 4 feature subspaces:
  1. *Goal subspace (6 dimensions, one-hot):* Muscle gain, Fat loss, Endurance, General fitness, Strength improvement, Flexibility & mobility.
  2. *Workout type / category subspace (4 dimensions):* Strength, Cardio, Plyometrics, Stretching.
  3. *Primary muscle groups subspace (8 dimensions, multi-hot):* Chest, Back, Legs, Shoulders, Arms, Core, Full Body, Cardio/Systemic.
  4. *Normalized duration fit (1 dimension):* `min(session_duration, user_duration) / max(session_duration, user_duration)`.
  Cosine Similarity is computed over the concatenated vector. Primary goal tiering is applied prior to tie-breaking.
- **Implementation Impact:** Non-blocking for documentation; must be locked before coding ranking evaluation.

### Q-002: Backend Database Access Technology in FastAPI
- **Status:** RESOLVED — Supabase Data API with caller JWT and RLS
- **Priority:** Medium
- **Source:** SRS §2.1, §5.1; PRD §15, §22
- **Question:** Should FastAPI use `supabase-py` (PostgREST HTTP client), `asyncpg` (direct PostgreSQL connection pool), or a hybrid?
- **Reason:** Supabase provides both PostgREST HTTP APIs and direct PostgreSQL connection strings (port 5432 / 6543 pooler).
- **Affected documents:** ARCHITECTURE.md, DATABASE.md, SETUP.md
- **Proposed Solution:** 
  Use `supabase-py` for user-scoped PostgREST requests with the verified caller JWT. Account deletion runs in a JWT-protected Edge Function with server-managed admin credentials. The app runtime does not need the database password.
- **Implementation Impact:** Non-blocking for documentation; establishes clean separation of concerns.

### Q-003: Duplicate Completion Idempotency Mechanism
- **Status:** PROPOSED
- **Priority:** Medium
- **Source:** SRS §3.8 (HIST-04), §4.5, §8.1; PRD §12.1
- **Question:** How exactly should the API identify and handle duplicate completion submissions?
- **Reason:** SRS states duplicate submissions must not create duplicate history and mentions either client idempotency key or HTTP 409 conflict.
- **Affected documents:** API.md, DATABASE.md, TESTING.md
- **Proposed Solution:**
  Endpoint `POST /api/history` accepts an optional `idempotency_key` (UUID generated by client on session completion click) and checks if the same user completed the same `workout_id` within a 10-minute cooldown window. If the exact same idempotency key is submitted, return the existing record with HTTP 200 (idempotent success). If a rapid duplicate submission without a key occurs within 60 seconds, return HTTP 409 `DUPLICATE_COMPLETION`.
- **Implementation Impact:** Non-blocking; provides deterministic client behavior.

### Q-004: Storage Format for Optional General Nutrition Guidance
- **Status:** PROPOSED
- **Priority:** Low
- **Source:** SRS §3.10; PRD §13
- **Question:** Should nutrition guidance articles be stored in a PostgreSQL table or static verified JSON/Markdown assets in the backend?
- **Reason:** Nutrition guidance is static, curated, non-medical, and does not require per-user persistence.
- **Affected documents:** ARCHITECTURE.md, DATABASE.md, FEATURES.md
- **Proposed Solution:**
  Store pre-reviewed nutrition educational modules as structured JSON/Markdown assets bundled in the backend (`app/content/nutrition.json`), served via `GET /api/nutrition` and `GET /api/nutrition/{goal}`. This avoids unnecessary database tables while maintaining review auditability.
- **Implementation Impact:** Non-blocking.

---

## 5. Assumptions and Their Impact

1. **ASSUMPTION-01 (Session Catalogue Size):** The MVP target catalogue consists of approximately 30 approved workout sessions derived from Free Exercise DB exercises, with at least 5 sessions per primary goal. *Impact:* If catalogue coverage is uneven for a particular goal/equipment combination during evaluation, the API returns HTTP 200 with an empty list (`[]`) and transparent explanation as required by REC-15.
2. **DECISION-02 (Token Verification):** FastAPI validates bearer tokens with Supabase Auth `get_user(token)` and derives the user ID from the verified response. Invalid tokens fail with 401; unavailable or unconfigured Auth fails closed with 503.
3. **DECISION-03 (Account Deletion Authority):** FastAPI calls the JWT-protected Supabase `delete-account` Edge Function. The function verifies the bearer token, derives the user ID, then calls `auth.admin.deleteUser`; the service key remains in Supabase-managed function secrets. Foreign keys cascade profile and history rows.

---

## 6. Technical Risks & Mitigation Plan

| Risk ID | Description | Severity | Mitigation Strategy |
|---|---|---|---|
| **RSK-01** | Free Exercise DB lacks session-level compositions | High | Hand-curate and validate 30 complete sessions with explicit sequences, sets, reps, and rest periods using approved exercise IDs. |
| **RSK-02** | User attempts to bypass safety hold via direct API calls | Critical | FastAPI recommendation controller loads profile directly from database using token-derived `user_id` and rejects before candidate query if hold is active. |
| **RSK-03** | Service role key leakage | Critical | Keep service-role key in Supabase-managed function secrets; never expose in Vite client or normal FastAPI config. |
| **RSK-04** | Cosine Similarity fails on zero vector | Medium | Explicit mathematical safeguard: check vector magnitude `norm(v) == 0`. Fall back to primary-goal match tier and stable `workout_id` sorting. |
| **RSK-05** | Supabase network latency skews local latency metric | Medium | Measure recommendation pipeline latency in FastAPI excluding external network hop, and report external DB latency separately per NFR-PERF-02. |

---

## 7. Change History

- **2026-10-28 (v1.0.0):** Initial comprehensive Context record established from approved SRS v1.0 and PRD v1.0. Identified confirmed requirements, non-applicability of Agents/MCP, and registered Q-001 through Q-004.
- **2026-10-29 (v1.1.0):** Added confirmed requirement REQ-CONF-15: Public Landing Page with Hero Section, value pillars, and 3-step pipeline walkthrough. Updated DESIGN.md, FEATURES.md, PLAN.md, README.md, and MASTER-DEVELOPMENT-PROMPT.md.
- **2026-11-14:** Supabase Auth token verification, caller-JWT Data API persistence, the JWT-protected account deletion function, least-privilege RLS grants, real source exercise ingestion, and removal of the demo/mock runtime were started. Workout sessions remain unseeded until reviewed prescriptions are available.
