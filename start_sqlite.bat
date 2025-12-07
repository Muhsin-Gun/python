@echo off
echo ================================================
echo Trading AI - Starting with SQLite
echo ================================================
echo.

set DB_TYPE=sqlite
set PORT=5001

echo Database: SQLite
echo Port: %PORT%
echo.
echo Starting server...
echo.

python app.py

pause
