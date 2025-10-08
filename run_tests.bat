@echo off
echo 🧪 ASK_GILLU Quick Test Runner
echo.

echo 📋 Available Test Options:
echo   1. Run all tests
echo   2. Run quick tests (Unit + API)
echo   3. Run specific test suite
echo   4. Run backend API tests only
echo   5. Run integration tests only
echo   6. Exit
echo.

set /p choice=Choose an option (1-6): 

if "%choice%"=="1" (
    echo.
    echo 🚀 Running all tests...
    python run_tests.py
) else if "%choice%"=="2" (
    echo.
    echo ⚡ Running quick tests...
    python run_tests.py --quick
) else if "%choice%"=="3" (
    echo.
    echo 📝 Available test suites:
    echo   - unit      (Unit tests)
    echo   - api       (Backend API tests)
    echo   - integration (Integration tests)
    echo   - performance (Performance tests)
    echo.
    set /p suite=Enter test suite name: 
    echo.
    echo 🧪 Running !suite! tests...
    python run_tests.py --test !suite!
) else if "%choice%"=="4" (
    echo.
    echo 🔌 Running backend API tests...
    python run_tests.py --test api
) else if "%choice%"=="5" (
    echo.
    echo 🔗 Running integration tests...
    python run_tests.py --test integration
) else if "%choice%"=="6" (
    echo.
    echo 👋 Goodbye!
    exit /b 0
) else (
    echo.
    echo ❌ Invalid choice. Please run the script again.
    pause
)

echo.
echo 📊 Test execution completed!
pause
