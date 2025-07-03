@echo off
echo Collecting static files...

REM Activate virtual environment
call .\venv\Scripts\activate

REM Set environment variables
if exist .env (
    for /f "tokens=*" %%i in (.env) do set %%i
)

REM Collect static files
python manage.py collectstatic --noinput

echo.
echo Static files have been collected!
echo.
pause
