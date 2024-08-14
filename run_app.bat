@echo off

REM Activate the virtual environment
call .\venv\Scripts\activate

REM Run the Flask application
start .\venv\Scripts\python.exe app.py

REM Wait for Flask to start (adjust the delay if necessary)
timeout /t 5 >nul

REM Start ngrok and expose port 5000
start /B C:\Users\HP\Documents\GitHub\passport-app\ngrok\ngrok.exe http 5000

REM Wait longer to ensure ngrok has started
timeout /t 10 >nul

REM Fetch the ngrok URL using PowerShell
for /f "tokens=*" %%A in ('powershell -Command "(Invoke-RestMethod -Uri http://localhost:4040/api/tunnels).tunnels[0].public_url"') do set "NGROK_URL=%%A"

REM Echo the ngrok URL
echo Ngrok URL: %NGROK_URL%

REM Copy the URL to the clipboard
echo %NGROK_URL% | clip

REM Keep the window open
pause
