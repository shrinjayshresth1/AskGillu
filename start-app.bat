@echo off
echo Starting ASK_GILLU Application...
echo.
echo Starting Backend Server...
cd backend
start "Backend Server" cmd /k "C:/Users/shrin/OneDrive/Desktop/CAG/.venv/Scripts/python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo Starting Frontend React App...
cd ../frontend-react
start "Frontend React App" cmd /k "npm start"

echo.
echo Both services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause
