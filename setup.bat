@echo off
title Finance Dashboard Setup
echo ========================================================
echo         Finance Dashboard API - One Click Setup         
echo ========================================================
echo.

echo [1/5] Creating Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment. Ensure Python is installed.
    pause
    exit /b
)

echo.
echo [2/5] Activating environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b
)

echo.
echo [3/5] Applying database migrations...
python manage.py makemigrations api
python manage.py migrate

echo.
echo [4/5] Seeding demo data (users and transactions)...
python manage.py seed_data

echo.
echo ========================================================
echo Setup Complete! 
echo.
echo Demo Users:
echo  1. Admin:   admin_user / Admin@123
echo  2. Analyst: analyst_user / Analyst@123
echo  3. Viewer:  viewer_user / Viewer@123
echo.
echo [5/5] Starting development server...
echo Open your browser to: http://127.0.0.1:8000/
echo ========================================================
echo.

python manage.py runserver
pause
