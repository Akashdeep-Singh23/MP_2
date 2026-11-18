# Product Requirements Document (PRD)
## Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning

**Version:** 1.0  
**Status:** Approved requirements baseline  
**Prepared for:** B.Tech AIML capstone project  
**Deployment model:** Local React/FastAPI demonstration with hosted Supabase services

---

## 1. Document Purpose

This Product Requirements Document defines the product goals, target users, scope, functional capabilities, safety boundaries, success criteria, and release requirements for the Personalized AI-Driven Fitness and Workout Recommendation System. It is the product-level source of truth for the MVP. Detailed API, database, validation, and implementation requirements are specified in the accompanying Software Requirements Specification (SRS).

The product is a fitness-information and workout-discovery tool. It is not a medical device, diagnostic system, or substitute for qualified medical or fitness advice.

## 2. Product Summary

The application collects a small set of fitness preferences and a mandatory safety-screening result, then recommends up to five reviewed workout sessions from a curated catalogue. The recommendation engine uses hard eligibility filters followed by a content-based Cosine Similarity ranker. Safety, difficulty, equipment, and data-quality constraints cannot be overridden by similarity scores.

Users can register and sign in with Supabase Auth, maintain a profile, view recommendation explanations, mark sessions as completed, review workout history, and view a dashboard with goal-wise completion counts and weekly completion trends. General non-medical nutrition guidance is available as an optional section.

The first release is intended for a local demonstration: React + Vite and FastAPI run locally while Supabase Auth and PostgreSQL are hosted.

## 3. Problem Statement

People looking for workouts may receive recommendations that do not fit their current fitness level, equipment access, time available, goals, or safety circumstances. A catalogue of individual exercises is also insufficient by itself to recommend a coherent session. The application addresses these issues by curating complete workout sessions, enforcing eligibility rules, explaining recommendations using verified data, and recording explicitly completed sessions.

## 4. Product Goals

1. Recommend relevant, reviewed workout sessions from a controlled catalogue.
2. Enforce safety and eligibility rules before ranking.
3. Provide transparent, understandable reasons for recommendations.
4. Support six defined primary fitness goals.
5. Give users a simple profile, completion history, and progress dashboard.
6. Demonstrate a reproducible ML ranking method and compare it with a deterministic baseline.
7. Keep the MVP feasible for a student capstone and a local demonstration.

## 5. Non-Goals

The MVP will not:
- Diagnose conditions, assess medical readiness, or provide medical clearance.
- Claim that a workout is safe for a particular medical condition.
- Generate weekly/monthly training plans.
- Generate personalized meal plans or calculate calories, calorie deficits/surpluses, BMI, body composition, or personalized macro targets.
- Prescribe supplements or therapeutic diets.
- Integrate wearables, smart watches, social feeds, trainers, or community features.
- Use a conversational AI fitness coach.
- Guarantee muscle gain, fat loss, performance improvement, or other outcomes.
- Automatically treat missing equipment metadata as bodyweight compatibility.
- Invent missing exercise/session data or relax hard filters to fill the recommendation list.

## 6. Target Users and Primary Use Cases

### 6.1 Target users
- A user seeking a structured workout suitable for a selected fitness goal, level, equipment set, and time budget.
- A capstone evaluator reviewing the recommendation logic, safety enforcement, data quality, API, and evaluation results.
- An administrator/developer curating and reviewing exercise and workout-session records.

### 6.2 Primary use cases
1. Register and sign in.
2. Complete required profile setup and safety screening.
3. Edit goal, level, equipment, and duration.
4. Request recommendations and inspect explanations.
5. View a session's exercise sequence, instructions, sets/reps or duration, and rest.
6. Mark a workout as completed.
7. Review history and dashboard trends.
8. Open optional general nutrition guidance.
9. Confirm account deletion and have private account data removed.

## 7. Supported Goals

The application supports these six primary goals:
1. Muscle gain
2. Fat loss
3. Endurance
4. General fitness
5. Strength improvement
6. Flexibility and mobility

A goal is supported only to the extent that the approved session catalogue contains appropriate sessions. The application must report catalogue coverage and must not relabel unrelated sessions to claim coverage. Goal-specific session suitability requires manual review.

## 8. User Profile and Required Inputs

### 8.1 Mandatory inputs before recommendations
- Primary goal
- Fitness level: Beginner, Intermediate, or Advanced
- Available equipment, selected explicitly
- Available workout duration
- Completed safety screening

If any mandatory input is missing, invalid, or contradictory, the system asks the user to correct or complete it and does not generate recommendations.

### 8.2 Optional inputs
Age, height, weight, secondary goal, and other preferences are not required for MVP ranking. They must not be collected or used unless a documented feature genuinely needs them. Missing optional preferences are omitted from scoring, not treated as positive matches.

### 8.3 Duration
Available duration is configurable within a validated range of 5–180 minutes. Session duration is a soft ranking preference, not a hard cutoff by default. Sessions that exceed the user's available time may appear lower with a clear warning. Missing or unverified session duration makes the session ineligible until verified. Session duration must account for planned work, rest, and other required session components.

### 8.4 Equipment
The user explicitly selects from:
- Bodyweight only
- Dumbbells
- Resistance bands
- Barbell
- Bench
- Gym machines
- Kettlebells
- Cable machine
- Exercise ball
- Foam roller

The user's equipment is treated as a set of resources. Every session's complete equipment requirements must be available, unless an explicitly mapped, reviewed, and validated alternative is applicable. Empty equipment selection is not interpreted as bodyweight-only. Foam rollers and exercise balls are not interchangeable with resistance equipment.

## 9. Safety Requirements and Boundaries

### 9.1 Mandatory screening
Before personalized recommendations, users must complete a screening covering injury, current pain, and physical limitations.

### 9.2 Safety hold
An active injury or ongoing physical limitation activates a hold and pauses personalized workout recommendations. Current or unexplained pain also pauses recommendations and prompts appropriate professional guidance. The system does not diagnose, prescribe treatment, or assert that a session is safe.

A fully resolved historical injury does not automatically block recommendations when the user explicitly confirms that it is fully resolved and no ongoing limitation remains. Uncertainty or an ongoing restriction keeps the hold active.

### 9.3 Resuming
A hold is not cleared by elapsed time, reopening the app, changing preferences, or changing the goal. Resumption requires explicit user confirmation that the concern has resolved; this is not medical clearance. A new or unresolved concern reactivates the hold.

### 9.4 Potentially urgent symptoms
If the screening indicates potentially urgent symptoms such as chest pain, severe breathing difficulty, or fainting, the application must not provide workout recommendations and must present appropriate urgent-care guidance.

### 9.5 Enforcement and privacy
The backend enforces the hold on every recommendation request, independent of the UI. Users cannot bypass it by changing goal, equipment, duration, or switching to a generic workout mode. Store only the minimum screening/hold status needed for enforcement; do not retain detailed medical narratives unless a separately approved requirement establishes a necessity.

## 10. Recommendation Experience

### 10.1 Recommendation unit
The system recommends complete workout sessions, not isolated exercises.

### 10.2 Pipeline
1. Validate authentication and required profile fields.
2. Check safety-screening/hold state.
3. Load only approved, recommendation-ready sessions.
4. Apply strict hard eligibility filters.
5. Rank the eligible candidates.
6. Return up to five sessions, explanations, and relevant cautions.
7. If no session qualifies, return an empty result with a clear explanation.

### 10.3 Hard filters
- Safety hold must not be active.
- Session and its referenced exercises must be approved and valid.
- Session difficulty must be recognized and allowed by the user's level.
- All required equipment must be available or satisfied through a validated mapped alternative.
- Session duration must be verified.
- All mandatory session/exercise fields and references must be valid.
- Unknown/unrecognized difficulty, equipment, or required metadata excludes a record until reviewed.

### 10.4 Difficulty mapping
- Beginner user → Beginner sessions only.
- Intermediate user → Beginner and Intermediate sessions.
- Advanced user → Beginner, Intermediate, and Advanced sessions.

### 10.5 Ranking
Use content-based Cosine Similarity within the eligible candidate set. Primary-goal matches rank ahead of secondary-goal-only matches. Within these tiers, use similarity and documented soft-preference weights. Weights are configurable and provisional until evaluated. A similarity score is not a probability, medical assessment, or guarantee of suitability.

Duration is a soft preference: fitting sessions are preferred, while longer sessions may appear lower with a clear warning. Similarity cannot override hard eligibility or safety constraints. Handle zero vectors safely and use a deterministic tie-break (for example, stable workout ID).

### 10.6 Result count and determinism
Return at most five sessions. Return fewer if fewer qualify; return an empty list if none qualify. Never relax filters to fill the list. Given the same profile, approved catalogue, ranking configuration, and data version, the ordered results must be identical.

### 10.7 Explanation
Each recommendation must explain its match using verified profile and session data, such as goal match, difficulty compatibility, equipment compatibility, and duration fit. Do not fabricate reasons or expose unsupported claims.

## 11. Dataset and Content Curation

### 11.1 Source
The selected exercise-level source is Free Exercise DB:
- Repository: https://github.com/yuhonas/free-exercise-db
- Schema: https://github.com/yuhonas/free-exercise-db/blob/main/schema.json
- License: https://github.com/yuhonas/free-exercise-db/blob/main/LICENSE.md
- Combined exercise JSON: https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json

The project must verify the source licence and attribution requirements before redistributing data. The source contains individual exercises, not complete workout plans. The team must curate complete sessions from reviewed exercises.

### 11.2 Coverage target
Target approximately 30 approved workout sessions, aiming for at least five primary-goal sessions per each of the six goals. This is a dataset planning target, not an eligibility rule or guarantee. If coverage is lower, report it honestly and return fewer recommendations when necessary.

### 11.3 Data quality workflow
1. Automatically validate schema, required fields, allowed values, numeric ranges, unique IDs, and references.
2. Quarantine failing records.
3. Manually review exercise instructions, difficulty, muscles, movement pattern, equipment, and session coherence.
4. Approve records only after both automated validation and manual review.
5. Revalidate material edits before republishing.

Approval represents application/data-quality review, not clinical certification. Missing values must never be invented.

### 11.4 Required exercise fields
- Stable unique `exercise_id`
- Non-empty name
- Reviewed difficulty (Beginner/Intermediate/Advanced)
- Explicit verified equipment requirements; empty list only when bodyweight execution is verified
- Instructions
- Reviewed primary muscles where applicable
- Reviewed movement pattern where applicable; non-applicability documented
- Controlled valid exercise category
- Traceable source reference
- Review status approved before publication

Optional exercise fields may include secondary muscles, image URLs, aliases, force, and mechanic.

### 11.5 Required session fields
- Unique `workout_id`
- Name
- Primary goal from the six supported goals
- Reviewed difficulty
- Verified duration
- Complete required equipment
- Ordered sequence of valid exercise IDs
- Sets/reps or duration for every exercise
- Explicit rest seconds, including zero where appropriate
- Controlled workout type
- Instructions
- Source attribution
- Approved review status

Optional fields may include secondary goals, description, image URL, and tags.

## 12. Workout History and Dashboard

### 12.1 Completion rule
A workout counts as completed only when the user explicitly marks it complete. The application must prevent accidental duplicate completion records for the same completion action.

### 12.2 History
Authenticated users can view their own workout history. Each record stores the user, session reference, completion timestamp, and a minimal session snapshot sufficient to understand the historical session if the catalogue changes. The backend derives identity from the validated token and never trusts a client-supplied user ID.

### 12.3 Extended dashboard
The dashboard includes:
- Total completed workouts
- Recent activity
- Weekly completion counts/trends
- Goal-wise completed workout counts, grouped by the session's primary goal
- Empty state for users with no completed workouts

Weekly trends use the completion timestamp. Dashboard figures are descriptive and do not claim medical or fitness outcomes.

## 13. Nutrition Guidance

Nutrition guidance is optional and separate from workout recommendations. Skipping it must not block workouts. It provides general, non-medical education about balanced eating, protein-containing foods, carbohydrates, healthy fats, fruit and vegetables, hydration, and practical adaptable habits. Guidance may be goal-aware for muscle gain, fat loss, endurance, and general fitness, but must not prescribe restrictive diets or promise results.

No extra personal data is required merely to view guidance. The MVP excludes personalized meal plans, daily calorie estimates, deficits/surpluses, macro targets, BMI/body-composition calculations, supplement dosages, diagnosis, treatment, and therapeutic diets. Content must be reviewed before publication and use clear non-medical language. Users with medical nutrition needs should be directed to an appropriate qualified professional.

## 14. Authentication, Privacy, and Account Deletion

- Supabase Auth handles signup, login, and logout.
- Email verification is optional; users receive immediate access after successful signup.
- Supabase Auth is called directly from React. FastAPI validates the access token for protected endpoints.
- User profile and history are private and associated with the authenticated identity.
- Use Supabase Row Level Security (RLS) and server-side authorization to prevent cross-user access.
- The Supabase service-role key must remain server-side and must never be embedded in the frontend or committed to source control.
- Account deletion requires an authenticated, deliberate confirmation. A trusted backend process deletes the Supabase Auth identity and associated private records, including profile and history. The shared exercise/session catalogue is retained. Handle partial failures safely and do not claim success until the deletion operation succeeds.
- Collect the minimum personal data needed for the agreed features.

## 15. Technical Product Architecture

- **Frontend:** React + Vite.
- **Backend:** Python + FastAPI.
- **Authentication and database:** Hosted Supabase Auth + PostgreSQL.
- **Local demonstration:** React and FastAPI run locally; Supabase remains hosted.
- **API style:** JSON over HTTP, documented with FastAPI OpenAPI/Swagger.
- **Recommendation engine:** deterministic filtering and content-based Cosine Similarity.
- **Evaluation:** compare Cosine ranking with a deterministic baseline under the same hard filters.

Proposed core tables:
`profiles`, `exercises`, `workout_sessions`, `session_exercises`, `exercise_alternatives`, `workout_history`.

## 16. MVP Functional Requirements

- FR-01: Users can register, sign in, and sign out.
- FR-02: Users can create and edit the mandatory recommendation profile.
- FR-03: Users must complete safety screening before recommendations.
- FR-04: Backend safety holds block recommendation requests.
- FR-05: Only approved, validated sessions are recommendation candidates.
- FR-06: Apply hard difficulty, equipment, and data-quality eligibility filters.
- FR-07: Rank eligible sessions using the approved deterministic Cosine Similarity pipeline.
- FR-08: Return up to five results, never relaxing hard filters.
- FR-09: Show evidence-based explanations and duration cautions.
- FR-10: Users can view complete session details.
- FR-11: Users can mark sessions complete and view personal history.
- FR-12: Dashboard displays total, recent, weekly, and goal-wise completion metrics.
- FR-13: Optional general nutrition guidance is available.
- FR-14: Users can delete their account and associated private data.
- FR-15: API errors are consistent and do not leak secrets or internal traces.
- FR-16: Developers can validate, quarantine, review, and approve catalogue records.
- FR-17: The project includes automated tests and a documented evaluation report.

## 17. Non-Functional Requirements

### Security and privacy
- Protected endpoints require valid access tokens.
- Identity is derived from validated tokens, not request-body user IDs.
- RLS and backend authorization prevent cross-user profile/history access.
- Service-role secrets remain server-side.
- CORS allows only configured frontend origins.
- No secrets, stack traces, or raw SQL errors in client responses.

### Reliability and data integrity
- Invalid or incomplete records are not published to the recommender.
- Duplicate IDs and broken references are rejected or quarantined.
- Database/dependency failures return controlled errors.
- Account deletion handles partial failures and prevents further access.

### Performance
- Target p95 latency below 1 second for the documented recommendation pipeline on the documented development environment. Define measurement boundaries, workload, and run count; exclude external network latency where appropriate and report it separately. This is a measured target, not a guarantee for all deployments.

### Usability and transparency
- Explain missing required profile fields.
- Clearly communicate empty recommendation results and safety holds.
- Explanations use verified data and avoid guarantees.
- Provide empty dashboard states.

### Maintainability
- Document configuration, local startup, schema/migrations, API contracts, tests, ranking weights, and dataset provenance.
- Keep ranking weights configurable and versioned.
- Use controlled vocabularies and stable IDs.

## 18. Success Metrics and Evaluation

### 18.1 Acceptance metrics
- EV-01: Zero hard-constraint violations in the automated test suite.
- EV-02: All defined mandatory acceptance tests pass before release.
- EV-03: Never return more than five sessions; return all qualifying results up to five; return empty results when none qualify.
- EV-04: Defined missing, invalid, and contradictory input cases produce the expected validation behavior.
- EV-05: Identical profile, catalogue, and configuration produce identical ordered results.
- EV-06: Compare Cosine Similarity and baseline on the same synthetic profiles and candidate pools.
- EV-07: Report NDCG@5 for both rankers when adequate relevance labels exist.
- EV-08: Measure p95 latency below 1 second on a documented development environment.
- EV-09: Document dataset/session counts, at least 10 representative synthetic profiles, methods, labels, configuration, results, and limitations.

### 18.2 Baseline
The baseline applies the same hard eligibility filters, then ranks by primary-goal match, secondary-goal match, and deterministic tie-break. This isolates ranking differences rather than filter differences.

### 18.3 Relevance labels
A human reviewer labels each profile-session pair:
- 0 — Not relevant
- 1 — Slightly relevant
- 2 — Relevant
- 3 — Highly relevant

Report NDCG@5 where candidate pools and labels support it. Cosine Similarity is not required to beat the baseline; differences must be reported and investigated honestly. Note that human labels are subjective.

### 18.4 Test profiles and scope
Use at least 10 representative synthetic profiles. Include edge cases such as safety holds, missing fields, no compatible equipment, all difficulty levels, no eligible sessions, fewer than five candidates, equal scores, and repeated identical inputs. Measure recommendation-pipeline latency separately from external network/AI latency.

## 19. MVP Scope and Future Enhancements

### MVP
- React + Vite frontend
- FastAPI backend
- Supabase Auth and PostgreSQL
- Profile setup/editing
- Safety screening and backend hold enforcement
- Reviewed exercise catalogue and curated full sessions
- Hard eligibility filters and Cosine Similarity ranking
- Up to five recommendations with verified explanations
- Completion history and extended dashboard
- Optional general nutrition guidance
- Account deletion/private-data removal
- Standard errors, security tests, ranking baseline, NDCG@5 report, and latency measurement

### Future scope
- AI chatbot/fitness assistant
- Weekly or monthly training plans
- Personalized calorie/macronutrient calculations and meal plans
- Wearable integrations
- Advanced body measurements, analytics, and predictive models
- Social, trainer, or community features
- More complex ranking models beyond the evaluated baseline

## 20. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Source catalogue has exercises but not complete sessions | Curate coherent sessions manually; validate sequence, dose, duration, rest, and equipment |
| Inconsistent or missing equipment metadata | Map controlled vocabulary; quarantine unknown records; manually review |
| Limited coverage for one or more goals | Track coverage by primary goal; disclose gaps; do not relax filters |
| Cosine ranking adds little value over baseline | Compare on identical candidates and labels; report honestly; tune only with documented evaluation |
| Safety status is bypassed through frontend-only checks | Enforce hold in FastAPI for every recommendation request |
| Cross-user history/profile exposure | Validate JWT, use RLS and server-side authorization, test isolation |
| Supabase deletion partially fails | Design trusted deletion workflow, restrict access during failure, report status accurately |
| Relevance labels are subjective | Document rubric, reviewer process, and limitations |
| Local configuration leaks secrets | Use environment variables, `.env.example`, and Git exclusions; never commit secrets |

## 21. Release Readiness Checklist

- [ ] Required profile validation and safety screening work.
- [ ] Backend safety hold blocks all personalized recommendations.
- [ ] Catalogue records pass automated and manual review.
- [ ] Equipment alternatives are explicitly mapped and validated.
- [ ] Hard-filter suite has zero violations.
- [ ] Recommendation count, empty results, and determinism tests pass.
- [ ] Authentication, RLS, and cross-user access tests pass.
- [ ] History, duplicate completion handling, and dashboard calculations pass.
- [ ] Account deletion is tested, including failure behavior.
- [ ] Nutrition content is reviewed and within scope.
- [ ] Evaluation report contains at least 10 synthetic profiles, baseline comparison, NDCG@5 where supported, and p95 latency.
- [ ] Local setup, environment variables, schema/migrations, and API docs are complete.
- [ ] Source licence and attribution have been checked.

## 22. Approved Defaults and Open Implementation Notes

The following defaults are approved: email verification optional with immediate access; extended dashboard with goal-wise counts and completion trends; local demonstration with hosted Supabase; proposed six-table schema; approximately 30 approved sessions as a target; documented configurable ranking weights; explicit completion semantics; minimal safety state; authenticated account deletion; and documented local setup/security.

Implementation details such as exact cosine feature vector encoding, similarity weights, database column types, migration tool, and precise API payload schemas must be documented during implementation and tested. They must not weaken approved safety, eligibility, privacy, or determinism requirements.
