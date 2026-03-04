@echo off
echo ============================================
echo   Real-time Face Attendance System (Django)
echo ============================================
echo.

:: Activate virtual environment
call "%~dp0.venv\Scripts\activate.bat"

:: Move to django_app
cd /d "%~dp0django_app"

:: Apply any pending migrations
echo Applying migrations...
python manage.py migrate --run-syncdb
echo.

:: Start the server
echo Starting Django server at http://127.0.0.1:8000/
echo Press Ctrl+C to stop.
echo.
start "" http://127.0.0.1:8000/
python manage.py runserver 8000

pause
