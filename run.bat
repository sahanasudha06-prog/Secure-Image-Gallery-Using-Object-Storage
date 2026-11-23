@echo off
title Secure Image Gallery - Sahana
echo ========================================================
echo   Secure Image Gallery using Cloud Object Storage (S3)
echo   Project by Sahana
echo ========================================================
echo.
cd /d "%~dp0"
echo Starting application on http://localhost:5000 ...
python app.py
pause
