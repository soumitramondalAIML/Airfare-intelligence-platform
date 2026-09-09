@echo off

cd /d "D:\Smart India Hackathon\backend"

echo ========================================
echo Airfare Price Index - Daily Collection
echo Started: %date% %time%
echo ========================================

".venv\Scripts\python.exe" "scripts\run_daily_collection.py"

echo.
echo ========================================
echo Finished: %date% %time%
echo ========================================

pause