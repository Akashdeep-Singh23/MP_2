# Software Requirements Specification (SRS)
## Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning

**Version:** 1.0  
**Status:** Approved requirements baseline  
**System style:** React/Vite frontend, FastAPI backend, hosted Supabase Auth/PostgreSQL

---

## 1. Introduction

### 1.1 Purpose
This SRS defines the externally observable software behavior, interfaces, data requirements, constraints, and verification criteria for the MVP. It complements the PRD and is intended for implementation, testing, and capstone evaluation.

### 1.2 Scope
The system authenticates users, stores a fitness profile and minimal safety status, recommends eligible curated workout sessions using hard filters and content-based Cosine Similarity, records completed workouts, provides a dashboard and optional general nutrition guidance, and supports account deletion. It is not a medical or diagnostic system.

### 1.3 Definitions
- **Candidate session:** A curated workout session considered by the recommendation pipeline.
- **Eligible session:** A candidate that passes all hard filters.
- **Safety hold:** A state that blocks personalized workout recommendations.
- **Approved record:** A record that passed automated validation and manual review.
- **Cosine Similarity:** A vector similarity measure used to rank eligible sessions.
- **RLS:** Supabase Row Level Security.
- **NDCG@5:** Normalized Discounted Cumulative Gain evaluated over the top five ranked results.
- **Primary-goal match:** A session's primary goal equals the user's selected primary goal.
- **Secondary-goal match:** A session has a reviewed secondary-goal association matching a user's selected secondary goal, if that optional feature is implemented.

## 2. Overall Description

### 2.1 Product perspective
The application consists of:
1. React + Vite web client running locally for demonstration.
2. Python + FastAPI application server running locally.
3. Hosted Supabase Auth.
4. Hosted Supabase PostgreSQL database.
5. A deterministic recommendation module in the backend.
6. Data validation and curation workflow for exercise and session records.

The client calls Supabase Auth directly for authentication. Protected application APIs are called through FastAPI using a bearer access token. FastAPI validates the token before accessing protected data or performing user-specific operations.

### 2.2 User classes
- **Unauthenticated visitor:** Can access public landing/informational content and authentication screens; cannot request personalized recommendations or access private history.
- **Authenticated user:** Can manage their profile, complete safety screening, request recommendations when eligible, view session details, record completion, see personal history/dashboard, view optional nutrition guidance, and request account deletion.
- **Content curator/developer:** Imports, validates, reviews, quarantines, and approves catalogue records through controlled development/admin procedures. Public users do not receive write access to the shared catalogue.

### 2.3 Operating environment
- Frontend: React + Vite, modern desktop browser.
- Backend: Python + FastAPI, local development server.
- Data/auth: hosted Supabase PostgreSQL and Supabase Auth.
- Transport: HTTP/JSON for local development; HTTPS required for any non-local deployment.
- Configuration: environment variables; secrets excluded from source control.

### 2.4 Design and implementation constraints
- The MVP uses complete workout sessions as the recommendation unit.
- Hard filters execute before ranking.
- Cosine Similarity cannot override hard filters or safety holds.
- Only approved, recommendation-ready sessions may be ranked.
- Missing or ambiguous required metadata excludes/quarantines a record.
- The system returns no more than five sessions and never relaxes hard filters to fill results.
- The frontend is not a security boundary; the backend enforces access and safety rules.
- No service-role key may be exposed in the browser.
- Optional nutrition guidance is general and non-medical.
- Email verification is optional; successful signup grants immediate application access.

## 3. Functional Requirements

### 3.1 Authentication and session handling
**AUTH-01:** The system shall allow a user to register through Supabase Auth.  
**AUTH-02:** The system shall allow an existing user to sign in through Supabase Auth.  
**AUTH-03:** The system shall allow a signed-in user to sign out.  
**AUTH-04:** Email verification shall be optional for the MVP; a successful signup shall allow immediate access.  
**AUTH-05:** FastAPI shall validate the bearer access token on every protected endpoint.  
**AUTH-06:** If a token is missing, invalid, or expired, the API shall reject the request with HTTP 401 and a standard error response.  
**AUTH-07:** The backend shall derive the user identity from the validated token and shall not trust a user ID supplied in the request body or query string.  
**AUTH-08:** The system shall prevent access to another user's profile, history, or dashboard data through backend authorization and Supabase RLS.

### 3.2 Profile management and input validation
**PROF-01:** The system shall allow an authenticated user to create and update their profile.  
**PROF-02:** The mandatory recommendation profile shall contain primary goal, fitness level, explicit equipment selection, available workout duration, and completed safety screening.  
**PROF-03:** Primary goal shall be one of: Muscle gain, Fat loss, Endurance, General fitness, Strength improvement, Flexibility and mobility.  
**PROF-04:** Fitness level shall be one of: Beginner, Intermediate, Advanced.  
**PROF-05:** Available workout duration shall be validated within the configured 5–180 minute range.  
**PROF-06:** Equipment selection shall use the controlled vocabulary: Bodyweight only, Dumbbells, Resistance bands, Barbell, Bench, Gym machines, Kettlebells, Cable machine, Exercise ball, Foam roller.  
**PROF-07:** An empty equipment selection shall not be interpreted as bodyweight-only. The client shall request an explicit selection and the API shall reject a recommendation request with no equipment selection.  
**PROF-08:** If any mandatory profile field is missing or invalid, the system shall request correction and shall not generate recommendations.  
**PROF-09:** Invalid values shall be rejected rather than silently replaced by defaults.  
**PROF-10:** Contradictory input values shall be clarified or rejected.  
**PROF-11:** Age, height, weight, and other nonessential profile fields shall remain optional and shall not be collected unless a documented MVP feature requires them.  
**PROF-12:** Optional missing preferences shall be omitted from ranking rather than treated as positive matches.  
**PROF-13:** The system shall revalidate the current profile before each recommendation request.

### 3.3 Safety screening and holds
**SAFE-01:** The system shall require screening for injury, current pain, and physical limitations before personalized recommendations are available.  
**SAFE-02:** An active injury or ongoing physical limitation shall activate a safety hold.  
**SAFE-03:** Current or unexplained pain shall activate a safety hold and display appropriate professional-guidance messaging.  
**SAFE-04:** Potentially urgent symptoms, including chest pain, severe breathing difficulty, or fainting, shall block workout recommendations and trigger appropriate urgent-care guidance.  
**SAFE-05:** While a safety hold is active, every recommendation request shall be rejected before candidate ranking.  
**SAFE-06:** Changing goal, equipment, duration, or other preferences shall not clear or bypass a hold.  
**SAFE-07:** A hold shall not clear automatically due to elapsed time or app restart.  
**SAFE-08:** Resumption shall require explicit user confirmation that the concern has resolved; the application shall clarify that this confirmation is not medical clearance.  
**SAFE-09:** A fully resolved historical injury may be treated as non-blocking only when the user explicitly confirms it is fully resolved and no ongoing limitation remains. Uncertainty shall keep the hold active.  
**SAFE-10:** The backend shall enforce safety state independently of frontend behavior.  
**SAFE-11:** The system shall store only the minimal safety-screening/hold status needed for enforcement and shall avoid unnecessary detailed medical narratives.  
**SAFE-12:** Safety-hold responses shall use a stable error code such as `SAFETY_HOLD_ACTIVE`, HTTP 409, and non-diagnostic next-step guidance.

### 3.4 Catalogue validation and approval
**DATA-01:** Every exercise shall have a stable unique ID, name, reviewed difficulty, explicit verified equipment requirements, instructions, reviewed primary muscles where applicable, reviewed movement pattern where applicable, controlled exercise category, source reference, and review status.  
**DATA-02:** Every session shall have a unique ID, name, primary goal, reviewed difficulty, verified duration, complete equipment requirements, ordered exercise sequence, sets/reps or duration for each exercise, explicit rest seconds, controlled workout type, instructions, source attribution, and review status.  
**DATA-03:** The system shall validate required fields, allowed values, numeric ranges, unique IDs, and references automatically.  
**DATA-04:** Records that fail automated validation shall be quarantined and excluded from recommendation candidates.  
**DATA-05:** Records shall be manually reviewed for instructions, classification, equipment completeness, and session coherence before approval.  
**DATA-06:** Only records that pass automated validation and manual review shall be marked approved.  
**DATA-07:** Unknown or unrecognized difficulty, equipment, goal, or required metadata shall exclude a record until reviewed.  
**DATA-08:** Empty exercise equipment requirements shall be allowed only when bodyweight execution has been verified.  
**DATA-09:** Missing or unverified duration shall exclude a session until verified.  
**DATA-10:** Each session exercise reference shall resolve to a valid approved exercise.  
**DATA-11:** A material change to an approved record shall trigger revalidation and review before it is used again.  
**DATA-12:** Approval shall represent data/application review and shall not be represented as clinical certification.  
**DATA-13:** The catalogue shall preserve traceable source attribution and licence information for imported data.  
**DATA-14:** The planning target is approximately 30 approved sessions, aiming for at least five primary-goal sessions per supported goal. This target shall not alter eligibility logic.

### 3.5 Equipment compatibility and alternatives
**EQ-01:** The system shall treat user equipment as a set of available resources.  
**EQ-02:** A session shall be eligible only if every required item is available or satisfied by a specifically mapped, reviewed, and validated alternative.  
**EQ-03:** The system shall not infer that missing equipment metadata means bodyweight execution.  
**EQ-04:** An alternative shall have explicit mapping and its own equipment requirements shall be checked.  
**EQ-05:** Unknown, ambiguous, or unreviewed equipment requirements shall cause the affected record to be excluded.  
**EQ-06:** Equipment compatibility shall be re-evaluated for every recommendation request using the current profile.  
**EQ-07:** Foam roller and exercise ball requirements shall not be treated as interchangeable with resistance equipment.

### 3.6 Recommendation generation
**REC-01:** The recommendation unit shall be a complete workout session, not an individual exercise.  
**REC-02:** The system shall perform authentication, required-input validation, and safety-hold checks before ranking.  
**REC-03:** The system shall load only approved, recommendation-ready sessions and exercises.  
**REC-04:** The system shall apply all hard eligibility filters before calculating or using ranking scores.  
**REC-05:** Difficulty eligibility shall be: Beginner user → Beginner only; Intermediate user → Beginner and Intermediate; Advanced user → Beginner, Intermediate, and Advanced.  
**REC-06:** A candidate session shall be excluded if any hard constraint fails.  
**REC-07:** The ranking method shall use content-based Cosine Similarity over documented feature vectors.  
**REC-08:** Primary-goal matches shall rank ahead of secondary-goal-only matches.  
**REC-09:** Within the goal-match tier, the system shall use Cosine Similarity and documented configurable soft-preference weights.  
**REC-10:** Duration shall be a soft ranking preference by default. A session exceeding the available duration may appear lower with a clear warning; it shall not be treated as an exact fit.  
**REC-11:** The system shall safely handle zero vectors and other undefined similarity cases without crashing or producing non-finite scores.  
**REC-12:** The system shall use a deterministic tie-break, such as stable workout ID.  
**REC-13:** The system shall return at most five sessions.  
**REC-14:** If fewer than five sessions qualify, the system shall return all qualifying sessions; it shall not relax hard filters.  
**REC-15:** If no sessions qualify, the system shall return HTTP 200 with an empty result list and a clear explanation.  
**REC-16:** The system shall provide explanations based only on verified profile and session data.  
**REC-17:** Similarity scores shall not be described as probabilities, guarantees, or proof of safety.  
**REC-18:** Given the same profile, approved catalogue/data version, and ranking configuration, the ordered results shall be identical.  
**REC-19:** Changes to ranking weights or feature encoding shall be documented and versioned.  
**REC-20:** The system shall report catalogue coverage by primary goal during evaluation and shall not fabricate coverage.

### 3.7 Workout session detail
**SESSION-01:** The system shall expose details for each recommended session, including ordered exercises, instructions, sets/reps or duration, rest, duration, difficulty, equipment, and primary goal.  
**SESSION-02:** Session detail shall reflect approved catalogue data.  
**SESSION-03:** If a session becomes unavailable or unapproved, it shall not be newly recommended. Existing historical snapshots shall remain understandable.

### 3.8 Workout history
**HIST-01:** An authenticated user shall be able to mark a session as completed.  
**HIST-02:** A completion record shall be created only after explicit user action.  
**HIST-03:** The server shall derive the user ID from the validated token.  
**HIST-04:** The system shall prevent duplicate completion records for the same completion action using a defined idempotency or duplicate-detection rule.  
**HIST-05:** Users shall only read their own history.  
**HIST-06:** A history record shall include user reference, session reference, completion timestamp, and a minimal snapshot of relevant session details.  
**HIST-07:** History shall remain understandable if the current session catalogue changes.  
**HIST-08:** The system shall return the user's history in a documented deterministic order, newest first unless otherwise specified.

### 3.9 Dashboard
**DASH-01:** The dashboard shall show total completed workouts.  
**DASH-02:** The dashboard shall show recent activity.  
**DASH-03:** The dashboard shall show weekly completion counts/trends derived from completion timestamps.  
**DASH-04:** The dashboard shall show goal-wise completion counts grouped by the completed session's primary goal.  
**DASH-05:** The dashboard shall show a clear empty state when no workouts have been completed.  
**DASH-06:** Dashboard values shall be derived from completion records, not from recommendation views or uncompleted sessions.  
**DASH-07:** Dashboard content shall be private to the authenticated user.

### 3.10 Nutrition guidance
**NUT-01:** General nutrition guidance shall be optional and separate from workout recommendation requirements.  
**NUT-02:** Users shall be able to view general guidance without providing additional personal data solely for that purpose.  
**NUT-03:** Content may cover balanced nutrition, protein-containing foods, carbohydrates, healthy fats, fruit and vegetables, hydration, and practical habits.  
**NUT-04:** Guidance may be goal-aware for muscle gain, fat loss, endurance, and general fitness, without promising outcomes.  
**NUT-05:** The MVP shall not calculate calories, deficits/surpluses, macro targets, BMI, body composition, or personalized meal plans.  
**NUT-06:** The MVP shall not diagnose or treat conditions, prescribe therapeutic diets, prescribe supplement dosages, or recommend extreme restriction.  
**NUT-07:** Content shall be reviewed before publication and clearly labelled as general, non-medical information.

### 3.11 Account deletion
**DEL-01:** An authenticated user shall be able to initiate account deletion.  
**DEL-02:** Deletion shall require a deliberate confirmation step.  
**DEL-03:** A trusted backend workflow shall delete the Supabase Auth identity and associated private records, including profile and workout history.  
**DEL-04:** Shared catalogue data shall not be deleted when one user deletes their account.  
**DEL-05:** The backend shall not claim deletion succeeded until the operation is confirmed successful.  
**DEL-06:** Partial failures shall be handled safely, access to the account shall be restricted while deletion is unresolved, and the UI shall communicate status without exposing internal secrets.  
**DEL-07:** Workout history shall not be retained after deletion unless a separately documented and approved legal/operational requirement requires retention.

### 3.12 API errors and observability
**API-01:** API requests and responses shall use JSON.  
**API-02:** Errors shall use a consistent envelope with `error.code`, `error.message`, optional `error.details`, and `error.request_id`.  
**API-03:** The API shall not expose stack traces, raw SQL errors, secrets, or internal tokens in client responses.  
**API-04:** The API shall return appropriate HTTP status codes according to the status-code policy in Section 7.  
**API-05:** A request ID shall be included in error responses and logs where feasible.  
**API-06:** The system shall handle database timeouts, dependency unavailability, malformed JSON, invalid tokens, and validation errors gracefully.  
**API-07:** FastAPI OpenAPI/Swagger documentation shall be available in the development environment.  
**API-08:** CORS shall allow only configured frontend origins.  
**API-09:** Health endpoint shall report application health without revealing secrets or sensitive configuration.

## 4. External Interface Requirements

### 4.1 User interface
The UI shall provide:
- Registration, login, and logout screens.
- Profile setup and edit screens.
- Mandatory safety screening and clear hold states.
- Recommendation list with explanation and cautions.
- Session detail view.
- Explicit completion action.
- History list.
- Dashboard with total, recent, weekly, and goal-wise metrics.
- Optional nutrition guidance section.
- Account deletion confirmation and result state.
- Validation errors and empty states.

The UI shall not rely on frontend-only checks for authorization or safety enforcement.

### 4.2 API endpoints
The following endpoint set is approved as the initial API surface. Exact field schemas, pagination, and idempotency details must be defined in OpenAPI before implementation is considered complete.

| Method | Endpoint | Purpose | Authentication |
|---|---|---|---|
| `GET` | `/api/health` | Application health | Public or restricted, with no sensitive output |
| `GET` | `/api/profile` | Read current user's profile | Required |
| `PUT` | `/api/profile` | Create/update current user's profile | Required |
| `POST` | `/api/recommendations` | Request eligible workout sessions | Required |
| `GET` | `/api/history` | Read current user's history | Required |
| `POST` | `/api/history` | Record explicit workout completion | Required |
| `GET` | `/api/dashboard` | Read current user's dashboard metrics | Required |
| `DELETE` | `/api/account` | Delete current user's account/private data | Required, confirmed |

Supabase Auth endpoints are called directly by the frontend using the Supabase client; they are not duplicated as FastAPI routes in the MVP.

### 4.3 Recommendation request and response contract
The final schema must be published in OpenAPI. The logical request shall identify the user's current profile context or use the persisted profile; it shall not accept a trusted user ID from the client. The response shall include:
- `results`: ordered list of zero to five sessions
- Session ID and display fields
- Verified explanation reasons
- Duration-fit status or caution when applicable
- `message` or equivalent when no sessions qualify
- A configuration/data version where useful for reproducibility

The backend shall derive user identity from the validated token and load current stored profile/safety state. If request-level preferences are allowed, they must be validated and must not override safety state or the user's authorized profile.

### 4.4 Standard error envelope
Example:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Please provide a valid workout duration.",
    "details": {
      "field": "duration_minutes"
    },
    "request_id": "request-id"
  }
}
```
`details` is optional. Messages must be safe for end users; detailed diagnostics belong in protected server logs.

### 4.5 HTTP status conventions
- `200 OK`: successful read/update or recommendation response, including an empty eligible result list.
- `201 Created`: a newly created resource, where used.
- `400 Bad Request`: malformed request syntax or malformed JSON.
- `401 Unauthorized`: missing, invalid, or expired access token.
- `403 Forbidden`: authenticated user lacks permission.
- `404 Not Found`: resource not found or not accessible to the user.
- `409 Conflict`: safety hold, duplicate completion conflict, or incompatible state.
- `422 Unprocessable Entity`: structurally valid request with invalid field values.
- `429 Too Many Requests`: rate limit exceeded, if configured.
- `500 Internal Server Error`: unexpected server failure with safe generic message.
- `503 Service Unavailable`: required dependency temporarily unavailable.

The precise split between 400 and 422 shall be consistent across the implementation and documented.

## 5. Data Requirements

### 5.1 Logical schema
The approved proposed tables are:
1. `profiles`
2. `exercises`
3. `workout_sessions`
4. `session_exercises`
5. `exercise_alternatives`
6. `workout_history`

### 5.2 Table responsibilities
**profiles**
- Associates application profile and minimal safety state with the authenticated Supabase user.
- Stores primary goal, fitness level, explicit equipment selection, available duration, and any approved minimal screening/hold fields.
- Optional attributes must remain optional and minimized.
- Must not store unnecessary detailed medical narratives.

**exercises**
- Stores normalized exercise metadata, source provenance, controlled classifications, equipment requirements, instructions, and review status.
- Unique stable exercise ID.
- Only approved records are exposed to the recommendation engine.

**workout_sessions**
- Stores session-level fields including primary goal, difficulty, verified duration, complete equipment requirements, workout type, instructions, attribution, and review status.
- Unique stable workout ID.
- Only approved and validated records are eligible.

**session_exercises**
- Join table linking sessions to exercises with explicit sequence/order.
- Stores per-exercise prescription fields such as sets, reps, duration, and rest.
- Enforces valid references and stable ordering.

**exercise_alternatives**
- Maps an exercise or relevant requirement to a specifically reviewed alternative.
- Records alternative exercise reference, applicable context, review/validation status, and the alternative's equipment requirements.
- An alternative is used only when explicitly approved for the context.

**workout_history**
- Stores authenticated user reference, session reference, completion timestamp, and a minimal historical session snapshot.
- Must support duplicate-completion protection.
- Must be private to the owning user and removed on account deletion.

### 5.3 Integrity constraints
- IDs are unique and stable.
- Foreign keys/reference integrity are enforced.
- A session cannot be approved if required exercises or prescription fields are missing.
- A session cannot be recommendation-ready with unknown difficulty, incomplete equipment, or unverified duration.
- Controlled values must be validated at import and write time.
- Material edits to approved records trigger review.
- User-specific records must be scoped to the authenticated identity.

### 5.4 Data source and attribution
Free Exercise DB is the selected exercise-level source:
- https://github.com/yuhonas/free-exercise-db
- https://github.com/yuhonas/free-exercise-db/blob/main/schema.json
- https://github.com/yuhonas/free-exercise-db/blob/main/LICENSE.md
- https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json

Before import or redistribution, verify the current licence terms and include required attribution. The database is exercise-level; complete workout sessions must be curated and reviewed separately.

### 5.5 Data lifecycle
Imported data follows: ingest → automatic validation → quarantine failures → manual review → approval → recommendation-ready publication. Updated approved data must be revalidated before reuse. The engine must never silently fill missing required data.

## 6. Recommendation Algorithm Requirements

### 6.1 Processing sequence
1. Validate bearer token and derive authenticated user.
2. Load the user's current profile and minimal safety state.
3. Reject if required profile data is missing or invalid.
4. Reject if a safety hold is active.
5. Load approved sessions and referenced approved exercises.
6. Apply hard filters.
7. Construct documented profile/session feature vectors.
8. Compute Cosine Similarity for eligible candidates, handling zero vectors safely.
9. Apply goal-match priority tiers and documented soft-preference weights.
10. Sort deterministically, with stable ID tie-break.
11. Return up to five sessions and evidence-based explanations.

### 6.2 Hard eligibility rules
- Beginner → Beginner only.
- Intermediate → Beginner + Intermediate.
- Advanced → Beginner + Intermediate + Advanced.
- Every required equipment item must be available or satisfied by an approved mapped alternative.
- Unknown/unreviewed equipment or difficulty excludes the session.
- Missing/unverified duration excludes the session.
- Unapproved or structurally invalid session/exercise excludes the candidate.
- Active safety hold blocks the whole personalized recommendation request before ranking.
- No hard filter may be relaxed to fill the output.

### 6.3 Ranking rules
- Primary-goal matches are ranked ahead of secondary-goal-only matches.
- Cosine Similarity and configurable soft preferences rank candidates within the applicable tier.
- Available duration is a soft preference; sessions exceeding it may rank lower and must display a warning.
- Exact weights and vector encoding must be documented, versioned, and evaluated.
- Similarity scores must not be presented as probabilities or guarantees.
- If the feature vector norm is zero or the similarity is undefined, use a documented safe fallback within the eligible tier and deterministic tie-break; do not crash or emit NaN/Infinity.
- Same inputs, catalogue version, and ranking configuration produce the same ordered output.

### 6.4 Baseline
The baseline uses the same hard filters, then orders candidates by primary-goal match, secondary-goal match, and deterministic stable ID. The comparison must use the same synthetic profiles, eligible candidate pools, and relevance labels as the Cosine ranker.

## 7. Non-Functional Requirements

### 7.1 Performance
**NFR-PERF-01:** Target p95 recommendation-pipeline latency below 1 second on a documented development environment.  
**NFR-PERF-02:** The measurement report shall specify machine/software configuration, dataset size, run count, request workload, measurement boundaries, and percentile calculation.  
**NFR-PERF-03:** External network/dependency latency shall be reported separately when excluded from the pipeline metric.

### 7.2 Security
**NFR-SEC-01:** All protected API endpoints require a valid access token.  
**NFR-SEC-02:** The server derives user identity from the validated token.  
**NFR-SEC-03:** RLS and backend authorization prevent cross-user access.  
**NFR-SEC-04:** The Supabase service-role key is server-side only.  
**NFR-SEC-05:** CORS allows only configured frontend origins.  
**NFR-SEC-06:** Secrets must be supplied through environment configuration and excluded from version control.  
**NFR-SEC-07:** Client errors must not expose stack traces, raw SQL, internal tokens, or secrets.  
**NFR-SEC-08:** Account deletion must use a trusted server-side workflow.

### 7.3 Privacy
**NFR-PRIV-01:** Collect only data required for approved features.  
**NFR-PRIV-02:** Do not collect detailed medical narratives when a minimal screening/hold state is sufficient.  
**NFR-PRIV-03:** Private profile/history/dashboard data is accessible only to the owner and authorized server operations.  
**NFR-PRIV-04:** Account deletion removes the Auth identity and associated private records, subject to explicitly documented operational/legal constraints.

### 7.4 Reliability and robustness
**NFR-REL-01:** Database failures, timeouts, malformed requests, and invalid tokens result in controlled errors.  
**NFR-REL-02:** Invalid catalogue records are excluded from recommendation candidates.  
**NFR-REL-03:** No eligible results is a valid response, not a server failure.  
**NFR-REL-04:** Repeated equivalent requests with the same versioned inputs produce the same ordered results.  
**NFR-REL-05:** Duplicate completion submissions do not silently create duplicate history.

### 7.5 Usability and accessibility
**NFR-UX-01:** The UI shall identify missing or invalid required inputs.  
**NFR-UX-02:** Safety holds and urgent guidance shall be clear and non-diagnostic.  
**NFR-UX-03:** Recommendations shall show verified explanations and duration cautions.  
**NFR-UX-04:** Empty recommendation and dashboard states shall explain what the user can do next.  
**NFR-UX-05:** Destructive account deletion requires explicit confirmation.

### 7.6 Maintainability and documentation
**NFR-MAINT-01:** Document local startup, environment variables, migrations/schema, and Supabase setup.  
**NFR-MAINT-02:** Document API contracts through OpenAPI/Swagger.  
**NFR-MAINT-03:** Document data provenance, licence review, controlled vocabularies, curation rules, ranking configuration, and evaluation methodology.  
**NFR-MAINT-04:** Keep ranking weights configurable and versioned.

## 8. Error Handling

### 8.1 Required behavior
- Missing/invalid profile fields: return validation errors; do not recommend.
- Active safety hold: return HTTP 409 with `SAFETY_HOLD_ACTIVE`.
- No eligible sessions: return HTTP 200 with an empty `results` array and a clear message.
- Invalid/expired token: HTTP 401.
- Cross-user access: HTTP 403 or privacy-preserving 404, consistently applied.
- Duplicate completion: idempotent success or HTTP 409 according to the documented API contract.
- Database unavailable: HTTP 503 when a required dependency is unavailable.
- Unexpected exception: HTTP 500 with generic user-safe message and request ID.

### 8.2 Logging
Logs may include request ID, endpoint, status, timing, and non-sensitive diagnostic metadata. Logs must not include access tokens, service-role keys, secrets, or unnecessary detailed safety narratives.

## 9. Verification and Test Requirements

### 9.1 Test strategy
- Unit tests for validators, difficulty rules, equipment matching, duration warnings, vector construction, Cosine Similarity, zero-vector handling, ranking tiers, and tie-breaks.
- Integration tests for FastAPI endpoints, Supabase-backed data access, token validation, history creation, dashboard aggregation, and deletion behavior.
- Security tests for cross-user access, missing/invalid tokens, RLS, service-role secret handling, and frontend-origin CORS.
- Data-quality tests for missing fields, invalid enum values, duplicate IDs, broken references, unknown equipment, and review-status enforcement.
- End-to-end tests for signup/login, profile completion, screening, recommendation, completion, history, dashboard, and deletion.
- Evaluation tests using at least 10 representative synthetic profiles.

### 9.2 Mandatory acceptance tests
**AT-01:** Beginner user never receives Intermediate or Advanced sessions.  
**AT-02:** Intermediate user never receives Advanced sessions.  
**AT-03:** Advanced user may receive all three reviewed difficulty levels.  
**AT-04:** A session requiring unavailable equipment is excluded unless a validated alternative satisfies every requirement.  
**AT-05:** Empty equipment selection blocks recommendation generation.  
**AT-06:** Missing or unverified session duration excludes the session.  
**AT-07:** Unapproved or invalid records are never recommended.  
**AT-08:** Active safety hold prevents recommendation generation before ranking.  
**AT-09:** Changing goal/equipment/duration does not bypass a safety hold.  
**AT-10:** Potentially urgent symptoms block recommendations and display urgent-care guidance.  
**AT-11:** Fewer than five eligible sessions returns all eligible sessions without relaxing filters.  
**AT-12:** Zero eligible sessions returns HTTP 200 with an empty list and clear message.  
**AT-13:** No response contains more than five sessions.  
**AT-14:** Repeated identical requests against the same data/config produce identical ordered results.  
**AT-15:** Zero-vector/undefined similarity handling does not crash or emit non-finite scores.  
**AT-16:** Recommendation explanations contain only verified data.  
**AT-17:** A user cannot read another user's profile/history/dashboard.  
**AT-18:** Invalid or expired access tokens are rejected.  
**AT-19:** A completion record is created only after explicit completion action.  
**AT-20:** Duplicate completion submission follows the documented idempotency/conflict behavior.  
**AT-21:** Dashboard totals, goal-wise counts, and weekly trends match history data.  
**AT-22:** Account deletion removes the Auth identity and private profile/history records while preserving shared catalogue data.  
**AT-23:** Nutrition guidance remains optional and does not introduce prohibited calculations or medical prescriptions.  
**AT-24:** Malformed inputs and dependency failures return controlled errors without leaking internals.  
**AT-25:** CORS accepts configured frontend origin and rejects unconfigured origins.  
**AT-26:** All defined mandatory acceptance tests pass before release.

### 9.3 Ranking evaluation
- Create at least 10 representative synthetic profiles.
- Run both rankers over identical profile inputs and hard-filtered candidate pools.
- Label profile-session pairs on a 0–3 relevance scale: 0 not relevant, 1 slightly relevant, 2 relevant, 3 highly relevant.
- Report NDCG@5 for Cosine and baseline where candidate pools and labels support the metric.
- Report dataset size, primary-goal coverage, feature encoding, weights/configuration, profile construction, reviewer procedure, results, and limitations.
- Do not promise Cosine will outperform the baseline; investigate and report the observed outcome.
- State that human relevance labels are subjective.

### 9.4 Performance evaluation
Measure recommendation-pipeline latency over a documented number of runs on the documented development machine and dataset. Report p50 and p95 where feasible. Define whether authentication/database calls are included; report external network/dependency latency separately if excluded. The target is p95 below 1 second for the defined pipeline, not a universal deployment guarantee.

## 10. API Contract Summary

### 10.1 Endpoint list
| Method | Path | Request purpose | Expected response |
|---|---|---|---|
| GET | `/api/health` | Check service health | Health status without secrets |
| GET | `/api/profile` | Get current profile | Profile or documented empty state |
| PUT | `/api/profile` | Save profile | Validated saved profile |
| POST | `/api/recommendations` | Request recommendations | 0–5 ordered sessions, reasons, message |
| GET | `/api/history` | Read history | Current user's completion records |
| POST | `/api/history` | Mark a session complete | Created/idempotent completion result |
| GET | `/api/dashboard` | Get metrics | Totals, recent activity, weekly and goal-wise counts |
| DELETE | `/api/account` | Delete account/private data | Confirmed deletion status |

### 10.2 Contract implementation notes
- Exact Pydantic request/response models shall be implemented and exposed in OpenAPI.
- Protected endpoints derive user ID from the validated bearer token.
- Recommendation requests use persisted profile and safety state as the source of truth.
- If request-specific filters are supported, they cannot bypass mandatory profile checks or safety holds.
- `request_id` shall be attached to errors and useful logs.
- API payloads must not contain secrets or detailed medical narratives.

## 11. Proposed Database Schema Notes

This section defines logical responsibilities, not final SQL DDL. Exact column types, indexes, constraints, and migration syntax are implementation decisions that must preserve these requirements.

### 11.1 `profiles`
Suggested logical fields:
- `user_id` (primary key/foreign key to Supabase Auth identity)
- `primary_goal`
- `fitness_level`
- `equipment` (validated set/array or normalized equivalent)
- `available_duration_minutes`
- minimal screening status and safety-hold state
- created/updated timestamps

Optional attributes should not be added without a documented need.

### 11.2 `exercises`
Suggested logical fields:
- `exercise_id`
- `name`
- `difficulty`
- verified `equipment_requirements`
- `instructions`
- `primary_muscles`
- `movement_pattern`
- `exercise_category`
- `source_reference`
- `review_status`
- optional source-specific metadata

### 11.3 `workout_sessions`
Suggested logical fields:
- `workout_id`
- `name`
- `primary_goal`
- optional reviewed `secondary_goals`
- `difficulty`
- `duration_minutes`
- complete `required_equipment`
- `workout_type`
- `instructions`
- `source_attribution`
- `review_status`
- optional description/image/tags

### 11.4 `session_exercises`
Suggested logical fields:
- `workout_id`
- `exercise_id`
- `sequence_number`
- sets/reps or duration prescription
- `rest_seconds`
- any reviewed exercise-specific notes

The table must preserve order and require a valid prescription for every session exercise.

### 11.5 `exercise_alternatives`
Suggested logical fields:
- alternative mapping ID
- source exercise or applicable requirement
- alternative exercise ID
- applicability context
- verified alternative equipment requirements
- review status and provenance

Only approved mappings may satisfy equipment compatibility.

### 11.6 `workout_history`
Suggested logical fields:
- history ID
- `user_id`
- `workout_id`
- completion timestamp
- minimal session snapshot
- idempotency/deduplication key if used

RLS must scope rows to the owning user. Deletion must remove the user's records.

## 12. Deployment and Configuration

### 12.1 Local demonstration architecture
- Run React + Vite on a local development port.
- Run FastAPI on a local development port.
- Connect to hosted Supabase Auth/PostgreSQL.
- Configure CORS for the exact local frontend origin.
- Use HTTPS for any public/non-local deployment.

### 12.2 Environment configuration
Provide a `.env.example` with placeholder names only. Actual secrets must be kept in ignored local environment files or a secrets manager. Never commit:
- Supabase service-role key
- private database credentials
- signing keys
- production secrets

The frontend may contain only the Supabase project URL and the appropriate public/anon key intended for browser use, with RLS correctly configured. Privileged keys stay in FastAPI/server-side configuration.

### 12.3 Setup documentation
The repository shall document:
1. Prerequisites and supported runtime versions.
2. Installing frontend and backend dependencies.
3. Creating/configuring the Supabase project.
4. Applying schema migrations and RLS policies.
5. Setting environment variables.
6. Starting FastAPI and React locally.
7. Running tests.
8. Accessing OpenAPI/Swagger docs.
9. Importing, validating, reviewing, and approving dataset records.
10. Known limitations and troubleshooting.

## 13. Risks and Constraints

- Exercise source data may not map cleanly to the application's controlled vocabulary.
- Complete sessions require manual curation beyond importing the exercise source.
- Goal coverage and recommendation diversity depend on the size and quality of the approved catalogue.
- Relevance judgments are subjective and small-sample evaluation limits generalization.
- Local latency results do not imply production performance.
- Supabase configuration errors can cause authorization or RLS failures; test with separate accounts.
- Account deletion across Auth and application tables needs a trusted, carefully tested workflow.

## 14. Traceability Matrix

| Product objective | SRS requirements | Verification |
|---|---|---|
| Personalized recommendations | PROF-02–13, REC-01–20 | Unit, integration, acceptance, ranking evaluation |
| Safety enforcement | SAFE-01–12 | Safety state and bypass tests |
| Reliable catalogue | DATA-01–14, EQ-01–07 | Import validation and quarantine tests |
| User history | HIST-01–08 | API and integration tests |
| Progress dashboard | DASH-01–07 | Aggregation tests against known fixtures |
| Optional nutrition education | NUT-01–07 | Content review and scope tests |
| Privacy and deletion | AUTH-05–08, DEL-01–07, NFR-SEC, NFR-PRIV | Security and deletion tests |
| Reproducible ranking | REC-07–20 | Repeatability tests, baseline comparison |
| Capstone evaluation | EV goals in PRD, Section 9 here | NDCG@5 and latency report |
| Local demo | Section 12 | Clean setup walkthrough |

## 15. Requirements Baseline and Change Control

This SRS reflects the confirmed decisions:
- Email verification optional with immediate access.
- Extended dashboard with goal-wise counts and weekly completion trends.
- Local frontend/backend demonstration with hosted Supabase.
- Proposed tables: profiles, exercises, workout_sessions, session_exercises, exercise_alternatives, workout_history.
- Approximately 30 approved sessions as a target, aiming for at least five primary-goal sessions per supported goal.
- Content-based Cosine Similarity, strict hard filters, primary-goal priority, configurable documented soft-preference weights, and deterministic ordering.
- Mandatory safety screening and backend-enforced holds.
- Optional general non-medical nutrition guidance.
- Basic workout history, explicit completion semantics, account deletion, baseline comparison, NDCG@5 where supported, at least 10 synthetic profiles, and p95 latency target under one second on a documented development environment.

Any change must be documented and must not weaken safety holds, hard eligibility constraints, privacy/security requirements, data-quality approval, or deterministic behavior without explicit review and approval.
