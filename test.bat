@echo off
echo Running tests...

REM Activate virtual environment
call .\venv\Scripts\activate

REM Set environment variables
if exist .env (
    for /f "tokens=*" %%i in (.env) do set %%i
)

REM Set test settings
set DJANGO_SETTINGS_MODULE=fileshare.settings.test

REM Run tests
python manage.py test

echo.
pause
