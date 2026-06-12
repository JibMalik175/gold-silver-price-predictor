@echo off
echo Starting Gold & Silver Predictor...
echo The backend will serve the frontend on the same port.
start cmd /k "cd backend && uvicorn app.main:app --reload --port 8000"

echo Server is starting...
echo Once started, open http://localhost:8000 in your web browser!
