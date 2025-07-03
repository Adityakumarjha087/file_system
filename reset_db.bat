@echo off
echo Resetting database...

REM Activate virtual environment
call .\venv\Scripts\activate

REM Remove existing database
if exist db.sqlite3 (
    echo Deleting existing database...
    del db.sqlite3
)

REM Run migrations
echo Applying migrations...
python manage.py migrate

REM Create superuser
echo Creating superuser...
call createsuperuser.bat

echo.
echo Database has been reset!
echo.
pause
