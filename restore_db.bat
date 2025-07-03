@echo off
setlocal enabledelayedexpansion

echo Available backups:
echo -----------------
set /a count=0

REM List all backup files
for /f "tokens=*" %%f in ('dir /b /o-d backups\backup_*.sqlite3 2^>nul') do (
    set /a count+=1
    set "file[!count!]=%%f"
    echo [!count!] %%f
)

if %count% EQU 0 (
    echo No backup files found in the backups directory.
    pause
    exit /b 1
)

echo.
set /p choice="Select backup to restore (1-%count%): "

REM Validate input
if "%choice%"=="" (
    echo No selection made.
    pause
    exit /b 1
)

set /a choice=!choice! 2>nul
if !errorlevel! NEQ 0 (
    echo Invalid selection.
    pause
    exit /b 1
)

if !choice! LSS 1 if !choice! GTR %count% (
    echo Selection out of range.
    pause
    exit /b 1
)

set "backup_file=backups\!file[%choice%]!"

REM Create a backup of current database before restoring
if exist db.sqlite3 (
    echo Creating backup of current database...
    call backup_db.bat >nul
)

REM Restore the selected backup
echo Restoring from %backup_file%...
copy /Y "%backup_file%" db.sqlite3 >nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Database restored successfully from %backup_file%
    echo.
    echo Note: You may need to run migrations if the database schema has changed.
) else (
    echo.
    echo Failed to restore database!
)

echo.
pause
