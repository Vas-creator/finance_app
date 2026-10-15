@echo off
echo ========================================
echo   Personal Finance App
echo ========================================

cd /d "%~dp0"

if not exist venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    echo [2/3] Installing packages...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo [3/3] Done!
) else (
    echo venv found. Activating...
    call venv\Scripts\activate.bat
)

echo Starting Streamlit...
streamlit run app.py