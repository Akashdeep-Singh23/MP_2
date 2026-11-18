# AGENTS.md — Autonomous Agent Architecture & Applicability Specification

**Project:** Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning  
**Version:** 1.0.0  
**Status:** NOT APPLICABLE (Explicit Architectural Scope Exclusion)  
**Authority Sources:** [PRD.md](../PRD.md) §5, §19; [SRS.md](../SRS.md) §1.2, §2.4; [CONTEXT.md](../documentation/CONTEXT.md) §2 (REQ-CONF-13)  

---

## 1. Architectural Status: NOT APPLICABLE

Autonomous AI agents, conversational LLM fitness coaches, agentic reasoning loops, and multi-agent orchestration frameworks are **explicitly excluded from the MVP scope** of this project.

The recommendation engine is built upon **deterministic algorithmic filtering** combined with **content-based Cosine Similarity over structured feature vectors** in Python/FastAPI.

---

## 2. Justification for Exclusion

1. **Safety Enforcement & Medical Boundary Integrity (PRD §5, §9; SRS §1.2, §3.3):**
   - Autonomous LLM agents are prone to hallucinations, non-deterministic reasoning, and jailbreaking/prompt manipulation. In a fitness system dealing with physical injury, pain, or cardiovascular symptoms, allowing an autonomous agent to decide whether a workout is "safe" or negotiate with a user to bypass a safety hold represents an unacceptable health risk.
   - The safety hold must be an unyielding, deterministic, code-level boolean check (`SAFE-01` through `SAFE-12`) that returns HTTP 409 `SAFETY_HOLD_ACTIVE` before any recommendation calculations execute.
2. **Determinism and Reproducibility (PRD §4, §18; SRS §3.6 REC-18, §7.4 NFR-REL-04):**
   - The project is a B.Tech AIML capstone requiring reproducible evaluation against a baseline.
   - Requirement **REC-18** mandates: *"Given the same profile, approved catalogue/data version, and ranking configuration, the ordered results shall be identical."* Autonomous agents with temperature or dynamic prompt sequences violate this reproducibility requirement.
3. **Transparent & Auditable Explanations (PRD §10.7; SRS §3.6 REC-16):**
   - Match explanations must be derived from verified metadata (matching primary goal, difficulty level, available equipment, duration match) rather than generative synthetic rationale.

---

## 3. Disambiguation: Application Agents vs. Antigravity Coding Agents

It is critical to distinguish between two distinct concepts:
- **Application-Level AI Agents (Out of Scope):** An agentic feature embedded inside the fitness software (e.g., an LLM bot talking to the user or an autonomous background agent re-ranking workouts). **Status: NOT IN MVP.**
- **Development-Time AI Assistants (In Scope):** Antigravity and its subagents (e.g. Codebase Architect, Test Engineer) acting as pair-programmers during the software engineering and documentation process. This development workflow operates entirely outside the deployed runtime of the fitness application.

---

## 4. Post-MVP Exploration & Activation Triggers

Should a future release (v2.0+) consider introducing AI agents, the following prerequisites and triggers must be satisfied:

1. **Approved Clinical / Safety Guardrail Architecture:**
   - The agent must operate strictly *downstream* of the deterministic safety hold. The agent must have zero authorization to clear, modify, or evaluate safety holds.
2. **Strict Tool-Call Schema & Sandboxing:**
   - Any agent must interact with the system via controlled, read-only tools (e.g. querying the approved exercise catalogue) with zero direct write access to the database.
3. **Formal Evaluation Dataset:**
   - An established benchmark of at least 100 adversarial prompts attempting to bypass physical limitations, with a required 100% safety hold compliance rate.

Until these conditions and explicit user approvals are documented, no autonomous agent frameworks (e.g. LangChain, CrewAI, AutoGen) shall be added to this codebase.
