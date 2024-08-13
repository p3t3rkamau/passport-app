@echo off

REM Activate the virtual environment
call .\venv\Scripts\activate

REM Run the Flask application
start .\venv\Scripts\python.exe app.py

REM Wait for Flask to start (adjust the delay if necessary)
timeout /t 5 >nul

REM Expose port 5000 using ngrok and redirect the output to a file
start /B C:\Users\Peter\PycharmProjects\Image_Passport\ngrok\ngrok.exe http 5000 > ngrok_output.txt

REM Wait longer to ensure ngrok has started and the link is available
timeout /t 20 >nul

REM Debug: Check if ngrok_output.txt has content
type ngrok_output.txt

REM Extract the ngrok link and copy it to the clipboard
for /f "tokens=2 delims= " %%A in ('findstr "http" ngrok_output.txt') do set NGROK_URL=%%A
echo %NGROK_URL% | clip

REM Cleanup: Optionally delete the ngrok_output.txt file
del ngrok_output.txt

REM Keep the window open
pause
