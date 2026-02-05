@echo off
REM Local Development Script for Content Analytics Tool
REM Run this if Docker is not available

echo ============================================
echo  Content Analytics Tool - Local Development
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

echo [1/3] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)

echo [2/3] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

echo [3/3] Starting Streamlit app...
echo.
echo ============================================
echo  Dashboard will open at http://localhost:8501
echo  Press Ctrl+C to stop the server
echo ============================================
echo.
echo NOTE: Running without PostgreSQL/Redis
echo       Using sample data for demonstration
echo.

streamlit run app/streamlit_app.py --server.port=8501

pause
