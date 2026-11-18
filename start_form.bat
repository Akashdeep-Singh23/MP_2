@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"

if not exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
  echo Backend virtual environment was not found.
  echo Create it with: cd backend ^&^& python -m venv venv ^&^& venv\Scripts\python -m pip install -r requirements.txt
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules\vite\bin\vite.js" (
  echo Frontend dependencies were not found.
  echo Install them with: cd frontend ^&^& npm install
  pause
  exit /b 1
)

if not exist "%BACKEND_DIR%\.env" (
  echo Missing backend\.env. Copy backend\.env.example to backend\.env and configure Supabase.
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%\.env" (
  echo Missing frontend\.env. Copy frontend\.env.example to frontend\.env and configure Supabase.
  pause
  exit /b 1
)

echo Starting FORM API on http://127.0.0.1:8000
start "FORM API - 8000" /D "%BACKEND_DIR%" "%BACKEND_DIR%\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

echo Starting FORM frontend on http://127.0.0.1:5173
start "FORM Frontend - 5173" /D "%FRONTEND_DIR%" "%ComSpec%" /k npm run dev -- --host 127.0.0.1

echo Waiting for the development servers to start...
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5173/"

echo.
echo FORM is starting. Keep the API and frontend windows open while you use the app.
endlocal

