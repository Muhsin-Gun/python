@echo off
echo ================================================
echo XAMPP MySQL Status Checker
echo ================================================
echo.

echo Checking if MySQL is running...
tasklist | findstr /I "mysqld.exe" > nul
if errorlevel 1 (
    echo [NOT RUNNING] MySQL is NOT running
    echo.
    echo To start MySQL:
    echo 1. Open XAMPP Control Panel
    echo 2. Click Start next to MySQL
    echo 3. Wait for it to turn green
    echo.
    echo OR use SQLite instead no XAMPP needed:
    echo - Run: start_with_sqlite.bat
) else (
    echo [OK] MySQL is RUNNING
    echo.
    echo You can now run: start_with_mysql.bat
)

echo.
echo Checking if XAMPP is installed...
if exist "C:\xampp\mysql\bin\mysqld.exe" (
    echo [OK] XAMPP found at C:\xampp
) else (
    if exist "D:\xampp\mysql\bin\mysqld.exe" (
        echo [OK] XAMPP found at D:\xampp
    ) else (
        echo [NOT FOUND] XAMPP not found
        echo Install from: https://www.apachefriends.org/
    )
)

echo.
pause
