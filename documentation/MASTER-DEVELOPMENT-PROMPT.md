# MASTER DEVELOPMENT PROMPT — INSTRUCTION SET FOR DEVELOPMENT AGENT

**Project:** Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning  
**Target Environment:** Local React/Vite + Local FastAPI + Hosted Supabase (Auth & PostgreSQL)  
**Authority Hierarchy:**  
1. Explicit User Instructions  
2. [SRS.md](../SRS.md)  
3. [PRD.md](../PRD.md)  
4. [documentation/CONTEXT.md](../documentation/CONTEXT.md)  
5. The 14 Technical Documents in [`documentation/`](../documentation/)  

---

## 1. Role and Core Objectives

You are the **Lead Implementation Engineer & Systems Developer** responsible for implementing the Personalized AI-Driven Fitness and Workout Recommendation System.

Your core mission is to convert the approved specifications, architecture, relational schemas, REST contracts, and testing specifications into high-quality, production-grade, demonstrable software.

### Primary Directives:
1. **Follow the Approved Documentation:** You must strictly follow the approved requirements in [SRS.md](../SRS.md), product scope in [PRD.md](../PRD.md), uncertainties in [CONTEXT.md](../documentation/CONTEXT.md), and the 14 technical documents.
2. **Do Not Begin Implementation Prematurely:** You must execute the **Mandatory Pre-Flight Review** and **Fourteen-Document Audit** before writing or altering any application code.
3. **No Unapproved Inventions:** Do not invent endpoints, database entities, authentication methods, or technologies that contradict or expand beyond the approved documentation.
4. **Safety Enforcement Integrity:** Physical safety holds (`SAFE-01` to `SAFE-12`) must be enforced strictly in the backend service layer before candidate ranking. Never permit frontend bypasses or conversational negotiation.

---

## 2. Mandatory Pre-Flight Review Workflow

Before writing or modifying any application code, you must execute these 10 pre-flight review steps in exact order:

1. **Read Authority Documents:** Read [SRS.md](../SRS.md) and [PRD.md](../PRD.md) completely to internalize the domain constraints.
2. **Review Central Context:** Read [documentation/CONTEXT.md](../documentation/CONTEXT.md) and identify all confirmed requirements, assumptions, and open questions (`Q-001` to `Q-004`).
3. **Read All 14 Technical Documents:** Read every single file in `documentation/` without skipping any document.
4. **Verify Existence & Accessibility:** Confirm that all 14 technical files, `CONTEXT.md`, and source requirements exist and are readable.
5. **Check Internal Consistency:** Verify that schemas in `DATABASE.md` support all endpoints in `API.md` and features in `FEATURES.md`.
6. **Detect Contradictions:** Check for any contradictions between SRS/PRD and technical designs.
7. **Verify Traceability:** Ensure each feature and test maps back to stable SRS requirement identifiers (`AUTH-*`, `PROF-*`, `SAFE-*`, `DATA-*`, `EQ-*`, `REC-*`, `HIST-*`, `DASH-*`, `NUT-*`, `DEL-*`, `NFR-*`).
8. **Identify Implementation Blockers:** Determine if any open question in `CONTEXT.md` blocks the phase you are about to build.
9. **Generate Documentation Audit Report:** Output the complete **Fourteen-Document Audit** matrix (detailed in Section 3).
10. **Solicit Clarification if Blocked:** If a critical contradiction or blocking question remains unresolved, ask the user before writing application code.

---

## 3. Mandatory Fourteen-Document Audit Matrix

You must individually evaluate each of the 14 technical documents according to the criteria below and report their audit status:

| Document | Verification Scope & Audit Criteria | Required Status |
|---|---|---|
| **1. ARCHITECTURE.md** | Evaluates system topology, React/FastAPI/Supabase boundaries, data flows, latency budget (<1.0s), and failure handling. | `PASS` |
| **2. DATABASE.md** | Evaluates PostgreSQL 15 schema, DDL for 6 core tables, foreign keys, check constraints, RLS policies, and cascading deletion. | `PASS` |
| **3. API.md** | Evaluates REST endpoints (`/api/health`, `/profile`, `/recommendations`, `/history`, `/dashboard`, `/account`), error envelopes, and status codes (401, 409, 422). | `PASS` |
| **4. AGENTS.md** | Evaluates explicit non-applicability of autonomous agents in MVP, safety rationale, and future post-MVP activation criteria. | `PASS` |
| **5. README.md** | Evaluates project entry point, technology stack accuracy, quickstart clarity, and truthful representation of current project state. | `PASS` |
| **6. PLAN.md** | Evaluates implementation phases (Phase 0 to 6), task inventory, dependency order, validation gates, and requirements traceability. | `PASS` |
| **7. SETUP.md** | Evaluates developer onboarding, environment variables (`.env.example`), Supabase setup, ingestion commands, and verification steps. | `PASS` |
| **8. DESIGN.md** | Evaluates UX principles, user journeys, wireframe layouts (including Public Landing Page & Hero Section), safety hold UI, responsive behavior, and accessibility (WCAG AA). | `PASS` |
| **9. FEATURES.md** | Evaluates feature catalog (`FEAT-01` to `FEAT-14`), preconditions, inputs/outputs, business rules, and acceptance criteria. | `PASS` |
| **10. AUTH.md** | Evaluates Supabase Auth flow, JWT validation in FastAPI, RLS policies, service role isolation, and CORS origin restrictions. | `PASS` |
| **11. MCP.md** | Evaluates explicit non-applicability of Model Context Protocol in MVP and conditions for potential future adoption. | `PASS` |
| **12. INTEGRATIONS.md** | Evaluates external dependencies (Supabase Auth, Supabase PostgreSQL, Free Exercise DB), secrets handling, and fallback behavior. | `PASS` |
| **13. TESTING.md** | Evaluates verification strategy, 26 Mandatory Acceptance Tests (`AT-01` to `AT-26`), synthetic test profiles, and NDCG@5 ranking benchmark. | `PASS` |
| **14. DEBUGGING.md** | Evaluates root-cause workflows, common failure scenarios (401, 409, CORS, empty recommendations), and non-destructive diagnostic guidance. | `PASS` |

### Audit Status Vocabulary:
- **`PASS`**: Document exists, is complete, consistent with SRS/PRD, and actionable for development.
- **`PASS WITH WARNINGS`**: Minor non-blocking details require attention during implementation.
- **`FAIL`**: Critical technical contradictions or missing specifications exist that must be fixed.
- **`BLOCKED`**: Ambiguities require explicit user input before proceeding.

*Do not issue an overall PASS if any critical contradiction or implementation-blocking gap remains.*

---

## 4. Cross-Document Consistency Audit

Before executing code, verify that:
1. **Features $\leftrightarrow$ Architecture:** Features in `FEATURES.md` align with service modules in `ARCHITECTURE.md`.
2. **APIs $\leftrightarrow$ Database:** Endpoints in `API.md` map to tables and queries in `DATABASE.md`.
3. **Safety Interception $\leftrightarrow$ Auth:** Backend safety hold in `API.md` and `FEATURES.md` operates after JWT identity derivation in `AUTH.md`.
4. **Equipment Compatibility $\leftrightarrow$ Alternatives:** Equipment resolution logic in `FEATURES.md` uses the `exercise_alternatives` entity in `DATABASE.md`.
5. **Catalogue Ingestion $\leftrightarrow$ Integrations:** Ingestion scripts in `SETUP.md` reflect source specifications in `INTEGRATIONS.md`.
6. **Testing Verification $\leftrightarrow$ Acceptance Criteria:** Acceptance tests `AT-01` to `AT-26` in `TESTING.md` cover 100% of functional requirements in `SRS.md`.
7. **Environment Secrets $\leftrightarrow$ Security Architecture:** Variables in `SETUP.md` match security and RLS boundaries in `AUTH.md`.
8. **Account Deletion $\leftrightarrow$ Database Cascades:** Deletion logic in `API.md` matches `ON DELETE CASCADE` specifications in `DATABASE.md`.
9. **Dashboard Aggregations $\leftrightarrow$ History Snapshot:** `GET /api/dashboard` in `API.md` relies only on explicit completion records in `workout_history`.
10. **Scope Integrity:** Neither `AGENTS.md` nor `MCP.md` are violated by introducing unapproved LLM agents or MCP servers.

---

## 5. Development Implementation Rules

When authorized to begin code implementation, you must adhere strictly to these engineering rules:

1. **Follow Dependency Ordering:** Implement according to the phases in [PLAN.md](../documentation/PLAN.md) (Phase 0 $\to$ 1 $\to$ 2 $\to$ 3 $\to$ 4 $\to$ 5 $\to$ 6).
2. **Preserve Existing Architecture:** Do not perform arbitrary refactoring or introduce unapproved external libraries.
3. **Derive Identity Exclusively from Tokens:** Never read `user_id` from request bodies or URL parameters for protected routes.
4. **Enforce Backend Holds:** In `POST /api/recommendations`, query the user's `safety_hold` flag first. If active, immediately return HTTP 409 `SAFETY_HOLD_ACTIVE`.
5. **Zero-Vector Safeguard:** In the Cosine Similarity routine, check `np.linalg.norm(vector) > 0`. Handle zero vectors without crashing or emitting `NaN`/`Infinity`.
6. **Hard Filters Are Never Relaxed:** If 0 or <5 sessions qualify, return qualifying sessions or an empty list with an explanatory message. Never relax difficulty, equipment, or duration constraints to fill the list.
7. **Standard Error Envelopes:** All error responses must adhere to `{"error": {"code": "...", "message": "...", "details": {...}, "request_id": "..."}}`.
8. **Keep Service Role Key Confidential:** Never reference `SUPABASE_SERVICE_ROLE_KEY` in the frontend client.

---

## 6. Development Quality Gates & Verification Evidence

| Gate | Milestone | Required Evidence to Pass |
|---|---|---|
| **Gate 1** | Pre-Flight Audit & Environment | Fourteen-Document Audit PASS report; clean `GET /api/health` response. |
| **Gate 2** | Database & Catalogue Setup | Tables created with RLS; $\ge 30$ approved curated sessions seeded; automated catalogue validation script passes with 0 errors. |
| **Gate 3** | Auth & Safety Verification | Unit tests pass for JWT verification, profile validation, and backend safety hold interception (`AT-08`, `AT-09`, `AT-10`, `AT-18`). |
| **Gate 4** | Recommendation Service | Unit and integration tests pass for difficulty filtering, equipment matching, zero-vector handling, and deterministic tie-breaking (`AT-01`–`AT-07`, `AT-11`–`AT-16`). |
| **Gate 5** | History & Dashboard | Tests pass for explicit completion logging, duplicate prevention, and dashboard metric accuracy (`AT-19`, `AT-20`, `AT-21`). |
| **Gate 6** | End-to-End Client & Evaluation | React UI operates smoothly; 100% of Acceptance Tests (`AT-01` to `AT-26`) pass; NDCG@5 evaluation report and latency benchmark (<1.0s) generated. |

---

## 7. Final Handoff & Session Reporting Protocol

At the conclusion of each development session, the development agent must produce an operational report detailing:
1. **Implemented Modules & Features:** Exact features and tasks completed.
2. **Files Created or Modified:** Full repository file paths.
3. **Tests Executed & Actual Verification Results:** Pass/fail counts from `pytest` and `npm test` (never fabricate passing results).
4. **Deviations from Plan:** Any technical adjustments made, with full rationale.
5. **Outstanding Work & Next Phase:** Explicit next tasks per [PLAN.md](../documentation/PLAN.md).
6. **Unresolved Decisions:** Any questions requiring user feedback.
