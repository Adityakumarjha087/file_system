@echo off
setlocal enabledelayedexpansion

REM Get current date and time in YYYYMMDD_HHMMSS format
for /f "tokens=2 delims==. " %%G in ('wmic OS Get localdatetime /value') do set "dt=%%G"
set "timestamp=!dt:~0,8!_!dt:~8,6!"

REM Set backup filename
set "backup_file=backup_%timestamp%.sqlite3"

REM Check if database exists
if not exist db.sqlite3 (
    echo Database file (db.sqlite3) not found!
    pause
    exit /b 1
)

REM Create backups directory if it doesn't exist
if not exist "backups" mkdir backups

REM Create backup
echo Creating database backup...
copy /Y db.sqlite3 "backups\%backup_file%" >nul

if %ERRORLEVEL% EQU 0 (
    echo Backup created successfully: backups\%backup_file%
) else (
    echo Failed to create backup!
)

echo.
pause
