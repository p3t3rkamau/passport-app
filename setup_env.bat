@echo off

REM Check if pip is available; if not, install it
if not exist .\pythonembed\Scripts\pip.exe (
    echo Installing pip...
    .\pythonembed\python.exe get-pip.py
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    mkdir venv
    xcopy /E /I /Y myenv venv
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
