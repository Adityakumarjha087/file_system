@echo off
echo Creating superuser...

REM Activate virtual environment
call .\venv\Scripts\activate

REM Set environment variables
if exist .env (
    for /f "tokens=*" %%i in (.env) do set %%i
)

REM Create superuser with default credentials
python manage.py createsuperuserwithprofile --username=admin --email=admin@example.com --password=admin123 --noinput

echo.
echo Superuser created successfully!
echo Username: admin
echo Password: admin123
echo.
echo WARNING: Please change the default password immediately!
echo.
pause
