@echo off
echo Checking deployment settings...

REM Activate virtual environment
call .\venv\Scripts\activate

REM Set environment variables
if exist .env (
    for /f "tokens=*" %%i in (.env) do set %%i
)

REM Set production settings
set DJANGO_SETTINGS_MODULE=fileshare.settings.production

REM Run deployment checks
echo.
echo ===== Running deployment checks =====
python manage.py check --deploy

echo.
echo ===== Checking security settings =====
python manage.py check --deploy --fail-level WARNING

echo.
echo ===== Checking for pending migrations =====
python manage.py showmigrations --list

echo.
echo ===== Checking static files =====
python manage.py collectstatic --dry-run --noinput

echo.
echo ===== Deployment check complete =====
echo.
pause
