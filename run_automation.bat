@echo off
REM Simple batch file to run AI Document Controller automation
REM This doesn't require administrator privileges

cd /d "C:\AI Projects\Document Controller"

echo ========================================
echo   AI Document Controller Automation
echo ========================================
echo.

:MENU
echo Choose an option:
echo   1. Run Daily Automation
echo   2. Run Weekly Automation  
echo   3. Run Monthly Automation
echo   4. Start Continuous Scheduler
echo   5. Show Configuration
echo   6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto DAILY
if "%choice%"=="2" goto WEEKLY
if "%choice%"=="3" goto MONTHLY
if "%choice%"=="4" goto SCHEDULER
if "%choice%"=="5" goto CONFIG
if "%choice%"=="6" goto EXIT
echo Invalid choice. Please try again.
goto MENU

:DAILY
echo.
echo Running daily automation...
"C:\AI Projects\Document Controller\.venv\Scripts\python.exe" automation_launcher.py daily
echo.
pause
goto MENU

:WEEKLY
echo.
echo Running weekly automation...
"C:\AI Projects\Document Controller\.venv\Scripts\python.exe" automation_launcher.py weekly
echo.
pause
goto MENU

:MONTHLY
echo.
echo Running monthly automation...
"C:\AI Projects\Document Controller\.venv\Scripts\python.exe" automation_launcher.py monthly
echo.
pause
goto MENU

:SCHEDULER
echo.
echo Starting continuous scheduler...
echo Press Ctrl+C to stop
"C:\AI Projects\Document Controller\.venv\Scripts\python.exe" automation_launcher.py schedule
goto MENU

:CONFIG
echo.
echo Current Configuration:
echo =====================
type .env | findstr "AUTOMATION\|AUTO_\|THRESHOLD"
echo.
pause
goto MENU

:EXIT
echo.
echo Thank you for using AI Document Controller!
pause