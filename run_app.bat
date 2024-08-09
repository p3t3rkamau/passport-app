@echo off
REM Activate the virtual environment
call venv\Scripts\activate

REM Run the Flask application
python app.py

REM Keep the window open
pause
