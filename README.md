# FORM — Personalized Workout Planning

FORM is a workout planning and tracking web app built as a B.Tech AIML capstone. It matches curated workout sessions to a user’s goal, experience, available equipment, and time, with a safety screening step before recommendations.

## What it includes

- Email sign up and sign in with Supabase Auth
- Profile preferences and safety screening
- Workout recommendations filtered by goal, level, equipment, and duration
- Session details, exercise instructions, and a rest timer
- Workout completion history and progress summaries
- General educational nutrition guidance

Recommendations and progress are backed by the project’s Supabase data. The app does not use a demo account or fabricated workout records.

## Technology

- **Frontend:** React 18, Vite, Tailwind CSS
- **API:** FastAPI, Pydantic, NumPy, scikit-learn
- **Auth and database:** Supabase Auth and PostgreSQL
- **Exercise source:** [Free Exercise DB](https://github.com/yuhonas/free-exercise-db); attribution and license details are in [`data/raw/LICENSE.md`](data/raw/LICENSE.md).

## Repository layout

| Path | Contents |
| --- | --- |
| `frontend/` | React application and Supabase client |
| `backend/` | FastAPI endpoints, recommendation logic, and tests |
| `supabase/migrations/` | Ordered database schema and policy migrations |
| `database/` | Schema and row-level security reference SQL |
| `data/raw/` | Source exercise catalogue and attribution |
| `scripts/` | Catalogue ingestion, validation, and ranking evaluation tools |
| `documentation/` | Setup guide, API, architecture, auth, database, and design docs |

## Quick start

### Prerequisites

- Python 3.10 or newer
- Node.js and npm
- A Supabase project

### 1. Configure Supabase and environment files

Create a Supabase project and apply the SQL migrations in `supabase/migrations/` in filename order. Copy the example environment files and fill in the project URL and publishable/anon key:

```powershell
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env
```

Set the corresponding values in both files. Keep `SUPABASE_SERVICE_ROLE_KEY` (if needed for catalogue ingestion) only in `backend/.env`; never put it in the frontend environment. `.env` files are ignored by Git.

### 2. Start the API

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Start the frontend

In another terminal, from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Vite serves the site at `http://127.0.0.1:5173/`.

For catalogue ingestion, testing, deployment, and troubleshooting, see [`documentation/SETUP.md`](documentation/SETUP.md) and [`documentation/TESTING.md`](documentation/TESTING.md).

## Documentation

- [Feature overview](documentation/FEATURES.md)
- [Architecture](documentation/ARCHITECTURE.md)
- [API reference](documentation/API.md)
- [Authentication and authorization](documentation/AUTH.md)
- [Database and migrations](documentation/DATABASE.md)
- [Development plan](documentation/PLAN.md)
- [Full documentation index](documentation/README.md)

## Project status

This is an academic capstone project under active development. Review the [project context and open decisions](documentation/CONTEXT.md) before relying on it in a production or clinical setting. Workout and nutrition information is educational and is not medical advice.

