@echo off

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)

REM Check if pip is available; if not, install it
if not exist .\pythonembed\Scripts\pip.exe (
    echo Installing pip...
    .\pythonembed\python.exe get-pip.py
)

REM Check if virtual environment exists; if not, create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Upgrade pip (optional but recommended)
.\venv\Scripts\python.exe -m pip install --upgrade pip

REM Install dependencies
if exist requirements.txt (
    echo Installing dependencies...
    .\venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
    echo No requirements.txt found, skipping installation of dependencies.
)

echo Setup complete.
pause
