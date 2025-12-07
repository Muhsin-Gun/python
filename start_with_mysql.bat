@echo off
echo ================================================
echo Trading AI - MySQL Setup and Start
echo ================================================
echo.

echo Checking if XAMPP MySQL is running...
tasklist /FI "IMAGENAME eq mysqld.exe" 2>NUL | find /I /N "mysqld.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo MySQL is already running!
) else (
    echo MySQL is not running.
    echo.
    echo Please start MySQL from XAMPP Control Panel:
    echo 1. Open XAMPP Control Panel
    echo 2. Click "Start" next to MySQL
    echo 3. Wait for it to turn green
    echo 4. Then run this script again
    echo.
    pause
    exit /b 1
)

echo.
echo Running MySQL setup...
python setup_mysql.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Setup successful! Starting the application...
    echo.
    set DB_TYPE=mysql
    python app.py
) else (
    echo.
    echo Setup failed. Please check the errors above.
    pause
)
