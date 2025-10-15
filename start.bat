@echo off
echo ========================================
echo  Advanced Analysis for E-Commerce
echo  Starting application...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 from https://www.python.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo.
echo Installing dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Run the application
echo.
echo ========================================
echo  Starting Streamlit...
echo  App will open in your browser
echo  Press Ctrl+C to stop
echo ========================================
echo.

streamlit run app/main.py

REM Deactivate on exit
deactivate
