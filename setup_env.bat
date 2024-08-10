@echo off
REM Set the path to the embedded Python
set PYTHON_DIR=%~dp0pythonembed

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    "%PYTHON_DIR%\python.exe" -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Upgrade pip (optional but recommended)
python -m pip install --upgrade pip

REM Install dependencies
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo No requirements.txt found, skipping installation of dependencies.
)

echo Setup complete.
pause
