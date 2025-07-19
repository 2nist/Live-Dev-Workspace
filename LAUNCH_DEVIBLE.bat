@echo off
REM =============================================================================
REM Devible - Professional Max for Live IDE
REM Easy Launch Script for Windows
REM =============================================================================

echo.
echo  ████████╗ ███████╗ ██╗   ██╗ ██╗ ██████╗  ██╗     ███████╗
echo  ██╔══██║ ██╔════╝ ██║   ██║ ██║ ██╔══██╗ ██║     ██╔════╝
echo  ██║  ██║ █████╗   ██║   ██║ ██║ ██████╔╝ ██║     █████╗
echo  ██║  ██║ ██╔══╝   ╚██╗ ██╔╝ ██║ ██╔══██╗ ██║     ██╔══╝
echo  ██████╔╝ ███████╗  ╚████╔╝  ██║ ██████╔╝ ███████╗███████╗
echo  ╚═════╝  ╚══════╝   ╚═══╝   ╚═╝ ╚═════╝  ╚══════╝╚══════╝
echo.
echo  Professional Max for Live IDE - v2.0 Beta
echo  The Future of Visual Music Programming
echo.

REM Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found!
    echo.
    echo Please install Node.js 18+ from: https://nodejs.org
    echo.
    echo After installation, restart this script.
    pause
    exit /b 1
)

REM Check Node.js version
echo [INFO] Checking Node.js version...
for /f "tokens=1" %%i in ('node -v') do set NODE_VERSION=%%i
echo [INFO] Node.js version: %NODE_VERSION%

REM Navigate to project directory
cd /d "%~dp0\max-live-ide"

REM Check if package.json exists
if not exist "package.json" (
    echo [ERROR] package.json not found!
    echo [ERROR] Please ensure you're running this from the correct directory.
    pause
    exit /b 1
)

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo.
    echo [INFO] Installing dependencies... This may take a few minutes.
    echo [INFO] ⏳ Setting up Devible for first-time use...
    npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
    echo [SUCCESS] ✅ Dependencies installed successfully!
)

REM Start the development server
echo.
echo [INFO] 🚀 Starting Devible...
echo [INFO] Opening browser at http://localhost:3000
echo.
echo [INFO] Ready to create amazing Max for Live devices!
echo [INFO] Press Ctrl+C to stop the server when done.
echo.

REM Open browser after a short delay
start "" "http://localhost:3000"

REM Start the React development server
npm start

REM If we get here, the server was stopped
echo.
echo [INFO] Devible server stopped.
echo [INFO] Thanks for using Devible! 🎵✨
pause
