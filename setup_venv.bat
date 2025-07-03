@echo off
echo Setting up Python virtual environment...

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or later from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
call .\venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Virtual environment setup completed successfully!
    echo.
    echo Next steps:
    echo 1. Run create_env.bat to create a .env file
    echo 2. Run migrate.bat to apply database migrations
    echo 3. Run createsuperuser.bat to create an admin user
    echo 4. Run runserver.bat to start the development server
) else (
    echo.
    echo Failed to install dependencies. Please check the error messages above.
)

echo.
pause
