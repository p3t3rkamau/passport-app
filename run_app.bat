@echo off
REM Set the path to the embedded Python
set PYTHON_DIR=%~dp0pythonembed

REM Ensure the embedded Python is used by setting PATH
set PATH=%PYTHON_DIR%;%PATH%

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the Flask application using the virtual environment's Python
venv\Scripts\python.exe app.py

REM Keep the window open
pause
