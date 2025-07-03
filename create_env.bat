@echo off
echo Creating .env file...

REM Check if .env already exists
if exist .env (
    echo .env file already exists.
    echo.
    echo To create a new .env file, please delete or rename the existing one first.
    pause
    exit /b 1
)

REM Create new .env file
echo # Django Settings > .env
echo DEBUG=True >> .env
echo SECRET_KEY=your-secret-key-here >> .env
echo ALLOWED_HOSTS=localhost,127.0.0.1 >> .env
echo. >> .env
echo # Database >> .env
echo DB_NAME=db.sqlite3 >> .env
echo DB_USER= >> .env
echo DB_PASSWORD= >> .env
echo DB_HOST=localhost >> .env
echo DB_PORT= >> .env
echo. >> .env
echo # Email Settings >> .env
echo EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend >> .env
echo EMAIL_HOST=localhost >> .env
echo EMAIL_PORT=25 >> .env
echo EMAIL_USE_TLS=False >> .env
echo DEFAULT_FROM_EMAIL=webmaster@localhost >> .env

echo.
echo .env file has been created with default values.
echo Please edit it to set your configuration.
echo.
pause
