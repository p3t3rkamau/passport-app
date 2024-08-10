@echo off
REM Set the path to the embedded Python
set PYTHON_DIR=%~dp0pythonembed

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the Flask application
python app.py

REM Keep the window open
pause
