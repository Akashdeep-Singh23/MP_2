# Personalized AI-Driven Fitness & Workout Recommendation System Using Machine Learning

[![Architecture](https://img.shields.io/badge/Architecture-React%20%2B%20FastAPI%20%2B%20Supabase-blue)](../documentation/ARCHITECTURE.md)
[![Status](https://img.shields.io/badge/Status-Implementation%20In%20Progress-blue)](../documentation/CONTEXT.md)
[![License](https://img.shields.io/badge/License-Academic%20Capstone-green)](#licensing--attribution)

---

## 1. Project Overview & Problem Statement

This project is a B.Tech Artificial Intelligence & Machine Learning (AIML) capstone delivering a transparent, safety-first workout recommendation engine.

Traditional fitness recommendation platforms frequently present users with unvetted, disconnected exercises or unconstrained conversational AI models that can recommend inappropriate physical activities to injured users. 

This application solves these issues by:
1. **Curating Complete Workout Sessions:** Recommending structured, end-to-end sessions (composed of verified exercise sequences, sets/reps, duration, and rest intervals) from an approved catalogue.
2. **Deterministic Safety Gating:** Mandating physical screening before recommendations. Any active injury, pain, or physical limitation triggers an immediate backend safety hold (`SAFETY_HOLD_ACTIVE`, HTTP 409) that prevents recommendation generation.
3. **Hard-Filtered Content-Based Machine Learning:** Running content-based Cosine Similarity ranking strictly on candidate workouts that pass 100% of hard constraints (difficulty compatibility, 100% equipment availability, verified duration).
4. **Transparent Match Explanations:** Explaining every recommendation with factual, verifiable criteria (goal alignment, difficulty match, equipment availability, duration fit).
5. **Rigorous Academic Evaluation:** Comparing the Cosine Similarity ranker against a heuristic baseline using NDCG@5 across synthetic user profiles.

---

## 2. Core Capabilities & Feature Set

- **Public Landing Page & Hero Section:** Informational entry point with a recommendation-process overview, value pillars, and 3-step pipeline walkthrough.
- **User Authentication:** Sign up, sign in, and session management via Supabase Auth (JWT).
- **Mandatory Profile & Safety Screening:** Profile configuration covering primary fitness goal, experience level, explicit equipment inventory, workout duration, and injury/limitation screening.
- **Backend Safety Hold:** Hard rejection of recommendation requests when safety flags are active.
- **Session Recommendation Engine:** Deterministic hard filtering followed by Cosine Similarity ranking over multidimensional feature vectors; returns up to 5 qualifying sessions.
- **Session Detail & Execution:** Complete session breakdown including instructions, exercise order, sets, reps, and rest timers.
- **Workout History & Progress Tracking:** Explicit workout completion tracking with duplicate-submission protection.
- **Extended Analytics Dashboard:** Total completed workouts, recent history, weekly completion trends, and goal-wise completion breakdowns.
- **Optional Nutrition Guidance:** General, non-medical educational content on macronutrients, hydration, and meal pacing.
- **Account Deletion:** Deliberate, user-confirmed deletion of Supabase Auth identity and private profile/history records.

---

## 3. Technology Stack

| Layer | Technologies | Role |
|---|---|---|
| **Frontend Web Client** | React 18, Vite, TypeScript/JS, Tailwind CSS, `@supabase/supabase-js` | Interactive single-page user interface running locally on port 5173. |
| **Backend REST API** | Python 3.10+, FastAPI, Pydantic v2, Uvicorn, NumPy, Scikit-Learn | Business logic, safety validation, vector ranking, and REST endpoints on port 8000. |
| **Data Persistence & Auth** | Hosted Supabase (PostgreSQL 15 + GoTrue Auth) | Identity management, row-level security (RLS), relational database. |
| **Dataset Provenance** | Free Exercise DB (JSON source) | Base exercise library curated into ~30 complete approved sessions. |

---

## 4. Current Project Status

- **Current State:** React and FastAPI application code is implemented and being connected to Supabase Auth and PostgreSQL.
- **Catalogue State:** The public-domain Free Exercise DB source file is bundled under `data/raw/`. Importing exercises does not automatically approve them or invent workout prescriptions; reviewed sessions must be added before recommendations are available.
- **Configuration:** Live use requires a Supabase project, values in `backend/.env` and `frontend/.env`, and the SQL schema/RLS setup described in `SETUP.md`.

---

## 5. Technical Documentation Index

All technical design documents are maintained in the [`documentation/`](../documentation/) directory:

1. [ARCHITECTURE.md](../documentation/ARCHITECTURE.md) — System topology, component boundaries, data flow, and resilience.
2. [DATABASE.md](../documentation/DATABASE.md) — Relational schema, DDL, constraints, RLS policies, and data lifecycle.
3. [API.md](../documentation/API.md) — REST endpoint specifications, payloads, error envelopes, and status codes.
4. [AGENTS.md](../documentation/AGENTS.md) — Status and architectural justification for autonomous agent exclusion.
5. [PLAN.md](../documentation/PLAN.md) — Implementation roadmap, milestone gates, and task dependencies.
6. [SETUP.md](../documentation/SETUP.md) — Local developer onboarding, environment variables, and startup guide.
7. [DESIGN.md](../documentation/DESIGN.md) — UI/UX design system, user journeys, wireframe flows, and state handling.
8. [FEATURES.md](../documentation/FEATURES.md) — Detailed feature inventory, business rules, and acceptance criteria.
9. [AUTH.md](../documentation/AUTH.md) — Authentication flow, JWT validation, RLS, and security controls.
10. [MCP.md](../documentation/MCP.md) — Model Context Protocol applicability review (status: Not Applicable).
11. [INTEGRATIONS.md](../documentation/INTEGRATIONS.md) — External service dependencies (Supabase, Free Exercise DB).
12. [TESTING.md](../documentation/TESTING.md) — Test strategy, 26 mandatory acceptance tests, and NDCG@5 evaluation.
13. [DEBUGGING.md](../documentation/DEBUGGING.md) — Troubleshooting guide, diagnostic steps, and recovery procedures.
14. [CONTEXT.md](../documentation/CONTEXT.md) — Source of truth, decisions log, and open clarification records.
15. [MASTER-DEVELOPMENT-PROMPT.md](../documentation/MASTER-DEVELOPMENT-PROMPT.md) — Authoritative implementation guide and 14-document audit.

---

## 6. Development Quickstart

*(Refer to [SETUP.md](../documentation/SETUP.md) for full setup instructions.)*

```bash
# 1. Configure credentials using backend/.env.example and frontend/.env.example
#    Create a Supabase project and apply database/schema.sql and database/rls_policies.sql.

# 2. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. Import the source exercise catalogue (run from repository root after setting backend/.env)
cd ..
python scripts/ingest_catalogue.py

# 4. Frontend Setup
cd frontend
npm install
npm run dev
```

---

## 7. Licensing & Attribution

- Exercise data is sourced from [Free Exercise DB](https://github.com/yuhonas/free-exercise-db) under its open-source license.
- Project developed for academic purposes under the B.Tech AIML curriculum.
