@echo off
echo Starting Django development server...

REM Activate virtual environment
call .\venv\Scripts\activate

REM Set environment variables
if exist .env (
    for /f "tokens=*" %%i in (.env) do set %%i
)

REM Run the development server
python manage.py runserver

pause
