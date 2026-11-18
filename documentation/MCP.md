# MCP.md — Model Context Protocol Applicability Specification

**Project:** Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning  
**Version:** 1.0.0  
**Status:** NOT APPLICABLE (Explicit Architectural Scope Exclusion)  
**Authority Sources:** [PRD.md](../PRD.md) §5, §19; [SRS.md](../SRS.md) §1.2, §2.4; [CONTEXT.md](../documentation/CONTEXT.md) §2 (REQ-CONF-14)  

---

## 1. Architectural Status: NOT APPLICABLE

The **Model Context Protocol (MCP)** is **not part of the MVP release** of this project.

The application does not run any MCP clients, nor does it expose internal system tools, databases, or workout catalogues via an MCP server to external large language models (LLMs).

---

## 2. Justification for Non-Applicability

1. **Deterministic Machine Learning Scope (PRD §2, §10; SRS §6):**
   - The recommendation system relies entirely on hard eligibility filtering and content-based Cosine Similarity calculated over structured NumPy feature vectors in FastAPI.
   - There is no conversational AI agent, autonomous reasoning engine, or generative model that requires dynamic context retrieval or tool execution via MCP.
2. **Medical & Physical Safety Boundaries (PRD §9; SRS §3.3):**
   - Physical safety screening holds must be evaluated and enforced directly by backend service logic (`SAFE-01` to `SAFE-12`). Exposing safety evaluation or recommendation decisions as tool calls to an external LLM via MCP would introduce latency, non-deterministic failure modes, and security vulnerabilities without any engineering benefit.
3. **Academic Capstone Scope & Local Demonstration (PRD §4, §15):**
   - The system is architected as a lightweight, clean, and easily evaluable local React/FastAPI stack connected to hosted Supabase. Adding MCP infrastructure would introduce unnecessary architectural complexity without contributing to the project's core research question (evaluating Cosine Similarity vs. a deterministic baseline using NDCG@5).

---

## 3. Disambiguation: Application Architecture vs. IDE Development Workflow

- **Project Application Architecture (This Codebase):** Has **no MCP servers or clients**. FastAPI exposes a standard HTTP/JSON REST API (`/api/*`), not an MCP transport.
- **Antigravity / IDE Coding Assistant Environment:** The developer or code assistant operating within Antigravity may utilize MCP tools to interact with development environments. That tooling belongs entirely to the developer's external IDE configuration and is decoupled from the fitness software itself.

---

## 4. Conditions & Requirements for Future MCP Introduction (Post-MVP v2.0+)

Should future research phases explore adding an MCP server (e.g. allowing external AI fitness assistants to query the approved workout catalogue), the following constraints must be enforced:

1. **Read-Only Scope:**
   - Any MCP server must expose strictly read-only tools (e.g., `get_approved_exercises`, `get_session_details`).
   - The MCP server must **never** expose tools to bypass safety holds, alter user profiles, or delete user accounts.
2. **Pre-Filtering Boundary:**
   - Any session query tool exposed via MCP must enforce hard difficulty, equipment, and duration filters *before* returning data to the LLM.
3. **Authentication & Transport:**
   - All MCP connections must authenticate using secure tokens with scoped permissions, using stdio or authenticated SSE transports.
4. **Data Isolation:**
   - No private user health screening data, workout histories, or personal identifiable information (PII) shall ever be exposed as an MCP resource.
