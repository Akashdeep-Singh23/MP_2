# SETUP.md — Developer Onboarding & Environment Configuration Guide

**Project:** Personalized AI-Driven Fitness and Workout Recommendation System Using Machine Learning  
**Version:** 1.0.0  
**Status:** PROPOSED Setup Specification  
**Authority Sources:** [SRS.md](../SRS.md) §12; [PRD.md](../PRD.md) §15, §21  

---

## 1. System Requirements & Runtime Prerequisites

| Component | Minimum Version | Recommended Version | Verification Command |
|---|---|---|---|
| **Operating System** | Windows 10/11, macOS 12+, Ubuntu 20.04+ | Windows 11 / Ubuntu 22.04 | `systeminfo` or `uname -a` |
| **Python** | 3.10.x | 3.11.x | `python --version` |
| **Node.js** | 18.x LTS | 20.x LTS | `node --version` |
| **Package Manager** | npm 9.x | npm 10.x | `npm --version` |
| **Git** | 2.30+ | Latest | `git --version` |
| **Database & Auth** | Supabase Cloud Account | Free / Pro Plan | Browser access to `app.supabase.com` |

---

## 2. External Service Prerequisites: Supabase Setup

1. **Create Supabase Project:**
   - Log into [Supabase Console](https://app.supabase.com) and create a new project (e.g., `ai-fitness-capstone`).
   - Select your nearest region and choose a strong database password.
2. **Collect API Credentials:**
   - Navigate to **Project Settings $\to$ API**.
   - Note the **Project URL** (e.g., `https://xyzproject.supabase.co`).
   - Use the project's **publishable key** with its Project URL in React and FastAPI.
   - Keep the service-role/secret key in Supabase-managed Edge Function secrets; normal app requests do not need it.
   - Navigate to **Project Settings $\to$ API $\to$ JWT Settings** and note the **JWT Secret**.
3. **Configure Authentication:**
   - Navigate to **Authentication $\to$ Providers $\to$ Email**.
   - Enable Email provider.
   - For local demonstration speed, uncheck *"Confirm email"* (optional email verification per **AUTH-04**).

---

## 3. Environment Variable Configuration

### 3.1 Backend Configuration (`backend/.env`)

Create `backend/.env` based on `backend/.env.example`:

```ini
# Server Settings
APP_NAME="Personalized AI Fitness System"
APP_ENV="development"
PORT=8000
HOST="127.0.0.1"

# CORS Settings (Explicit local frontend origin)
ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"

# Supabase Credentials (from Supabase Dashboard)
SUPABASE_URL="https://<project-ref>.supabase.co"
SUPABASE_ANON_KEY="<publishable-or-anon-key>"
SUPABASE_SERVICE_ROLE_KEY=""

# Optional direct SQL tooling only; the API uses the Supabase HTTPS Data API instead.
DATABASE_URL=""

# Machine Learning / Ranking Parameters
DEFAULT_TOP_K=5
DURATION_WARNING_THRESHOLD_MINUTES=10
```

> [!CAUTION]
> Never commit `backend/.env` to Git. Ensure `.gitignore` includes `.env` and `*.pem`.

### 3.2 Frontend Configuration (`frontend/.env`)

Create `frontend/.env` based on `frontend/.env.example`:

```ini
# Supabase Public Client Credentials
VITE_SUPABASE_URL="https://YOUR_PROJECT_ID.supabase.co"
VITE_SUPABASE_ANON_KEY="YOUR_SUPABASE_ANON_KEY"

# Backend REST API URL
VITE_API_BASE_URL="http://127.0.0.1:8000/api"
```

> [!IMPORTANT]
> The frontend `.env` must **NEVER** contain the `SUPABASE_SERVICE_ROLE_KEY` or database connection strings.

---

## 4. Database Initialization & Seed Data

### 4.1 Apply Schema & RLS Policies
In the Supabase Dashboard, open the **SQL Editor**, and run the migration script:
1. Apply the ordered SQL files in `supabase/migrations/` (schema first, then least-privilege grants and RLS policies).

### 4.2 Run Dataset Ingestion and Session Curation
From the root workspace directory, run the Python ingestion CLI:

```powershell
# Activate backend virtual environment
cd backend
.\venv\Scripts\activate  # Windows (or `source venv/bin/activate` on Linux/macOS)

# From the repository root, with backend/.env configured:
python scripts/ingest_catalogue.py
python scripts/validate_catalogue.py
```

Imported source exercises are quarantined for review. Session plans are not generated from exercise-only source records; create and review complete sessions before setting them to `approved`.

Expected output:
```text
[SUCCESS] Ingested 180 exercises from source.
[SUCCESS] Seeded 30 workout sessions across 6 primary goals.
[SUCCESS] Automated Validation PASSED: 0 schema errors, 0 broken references.
[SUCCESS] 30 sessions marked review_status = 'approved'.
```

---

## 5. Local Execution Commands

### 5.1 Launch Backend Service (FastAPI)

```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 5.2 Launch Frontend Web Client (React + Vite)

In a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```
- Open application: [http://localhost:5173](http://localhost:5173)

---

## 6. Verification Steps

1. **Verify Backend Health:**
   Run in PowerShell:
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -Method Get
   ```
   *Expected Response:* `{"status": "healthy", "version": "1.0.0"}`
2. **Verify Frontend Loading:**
   Open `http://localhost:5173` in a browser. The landing page and authentication screen should render with no console errors.
3. **Verify Interactive Sign Up & Profile:**
   - Sign up with a test email (`testuser@example.com`).
   - Fill out the 5 mandatory profile attributes and clear the safety screening.
   - Request recommendations; verify that up to 5 workout cards render with match explanations.

---

## 7. Clean Installation & Troubleshooting

If you encounter environment issues:
```powershell
# Reset Python Virtualenv
cd backend
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Reset Node Modules
cd ..\frontend
Remove-Item -Recurse -Force node_modules, package-lock.json
npm install
```
*(For detailed runtime troubleshooting, consult [DEBUGGING.md](../documentation/DEBUGGING.md).)*
