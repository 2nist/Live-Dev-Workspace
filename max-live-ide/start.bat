@echo off
cd /d "C:\Users\CraftAuto-Sales\OneDrive\Documents\ALSE\max-live-ide"
echo Starting Max Live IDE...
echo Current directory: %cd%
echo Package.json exists: 
if exist package.json (echo Yes) else (echo No)
echo.
echo Attempting to start React development server...
node ".\node_modules\react-scripts\bin\react-scripts.js" start
pause
