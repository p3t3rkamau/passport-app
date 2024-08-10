@echo off

REM Run the Flask application using the embedded Python's path directly
call .\venv\Scripts\activate

.\venv\Scripts\python.exe app.py

REM Keep the window open
pause
