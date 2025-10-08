@echo off
cd /d "%~dp0backend"
call "%~dp0.venv\Scripts\activate.bat"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
