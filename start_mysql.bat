@echo off
echo ================================================
echo Trading AI - Starting with MySQL
echo ================================================
echo.

set DB_TYPE=mysql
set PORT=5001

echo Database: MySQL
echo Port: %PORT%
echo.
echo Starting server...
echo.

python app.py

pause
