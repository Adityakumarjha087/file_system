@echo off
echo Running migrations...

REM Activate virtual environment
call .\venv\Scripts\activate

REM Set environment variables
if exist .env (
    for /f "tokens=*" %%i in (.env) do set %%i
)

REM Run migrations
python manage.py makemigrations
python manage.py migrate

echo.
echo Migrations have been applied!
echo.
pause
