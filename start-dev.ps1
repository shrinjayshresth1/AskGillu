#!/usr/bin/env pwsh

# Start ASK_GILLU Backend and Frontend
Write-Host "🚀 Starting ASK_GILLU..." -ForegroundColor Green

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptDir

# Backend paths
$backendDir = Join-Path $projectRoot "backend"
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$frontendDir = Join-Path $projectRoot "frontend-react"

Write-Host "📁 Project root: $projectRoot" -ForegroundColor Yellow
Write-Host "🐍 Python path: $venvPython" -ForegroundColor Yellow

# Check if virtual environment exists
if (-not (Test-Path $venvPython)) {
    Write-Host "❌ Virtual environment not found at: $venvPython" -ForegroundColor Red
    Write-Host "Please create a virtual environment first." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
$envFile = Join-Path $projectRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ .env file not found. Please create it from .env.example" -ForegroundColor Red
    exit 1
}

# Start backend in background
Write-Host "🔥 Starting backend server..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($backendDir, $venvPython)
    Set-Location $backendDir
    & $venvPython -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
} -ArgumentList $backendDir, $venvPython

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "⚛️ Starting frontend..." -ForegroundColor Green
Set-Location $frontendDir
npm start

# When frontend closes, stop backend
Write-Host "🛑 Stopping backend..." -ForegroundColor Yellow
Stop-Job $backendJob
Remove-Job $backendJob
