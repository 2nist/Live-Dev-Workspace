@echo off
REM =============================================================================
REM Devible - Setup and Installer Script
REM Checks requirements and sets up development environment
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
echo  Setup and Installation Wizard
echo.

set SETUP_COMPLETE=0
set NODE_OK=0
set DOCKER_OK=0

REM Check Node.js
echo [CHECKING] Node.js installation...
where node >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=1" %%i in ('node -v') do set NODE_VERSION=%%i
    echo [OK] ✅ Node.js found: %NODE_VERSION%
    set NODE_OK=1
) else (
    echo [MISSING] ❌ Node.js not found
    echo [INFO] Required: Node.js 18 or higher
    echo [INFO] Download from: https://nodejs.org
)

echo.

REM Check npm
echo [CHECKING] npm installation...
where npm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=1" %%i in ('npm -v') do set NPM_VERSION=%%i
    echo [OK] ✅ npm found: %NPM_VERSION%
) else (
    echo [MISSING] ❌ npm not found (usually comes with Node.js)
)

echo.

REM Check Docker (optional but recommended)
echo [CHECKING] Docker installation...
docker --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    docker info >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] ✅ Docker is installed and running
        set DOCKER_OK=1
    ) else (
        echo [WARNING] ⚠️ Docker installed but not running
        echo [INFO] Start Docker Desktop for containerized deployment
    )
) else (
    echo [INFO] ℹ️ Docker not found (optional)
    echo [INFO] Docker enables easy deployment and isolation
    echo [INFO] Download from: https://docker.com/products/docker-desktop
)

echo.

REM Check Git
echo [CHECKING] Git installation...
where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] ✅ Git found
) else (
    echo [WARNING] ⚠️ Git not found
    echo [INFO] Git enables version control and updates
    echo [INFO] Download from: https://git-scm.com
)

echo.

REM Check project structure
echo [CHECKING] Project structure...
if exist "max-live-ide\package.json" (
    echo [OK] ✅ Devible project structure found
) else (
    echo [ERROR] ❌ Devible project structure not found
    echo [ERROR] Please ensure you're running this from the ALSE directory
    echo [ERROR] Expected: max-live-ide\package.json
    pause
    exit /b 1
)

echo.

REM Summary and recommendations
echo =============================================================================
echo  SETUP SUMMARY
echo =============================================================================

if %NODE_OK% EQU 1 (
    echo ✅ READY: Node.js development environment
    echo    → Use LAUNCH_DEVIBLE.bat for direct development
) else (
    echo ❌ MISSING: Node.js required for development
    echo    → Install Node.js 18+ from https://nodejs.org
    echo    → Restart this setup after installation
)

echo.

if %DOCKER_OK% EQU 1 (
    echo ✅ READY: Docker containerized environment
    echo    → Use LAUNCH_DEVIBLE_DOCKER.bat for isolated deployment
) else (
    echo ℹ️ OPTIONAL: Docker for easy deployment
    echo    → Install Docker Desktop for production-like environment
    echo    → Recommended for beta testing and deployment
)

echo.
echo =============================================================================
echo  NEXT STEPS
echo =============================================================================

if %NODE_OK% EQU 1 (
    echo 1. 🚀 QUICK START: Double-click "LAUNCH_DEVIBLE.bat"
    echo    → Starts development server on http://localhost:3000
    echo    → Automatically installs dependencies on first run
    echo    → Opens browser when ready
    echo.
    echo 2. 🐳 DOCKER START: Double-click "LAUNCH_DEVIBLE_DOCKER.bat"
    echo    → Starts containerized version (if Docker available^)
    echo    → Isolated environment with all services
    echo    → Recommended for production testing
    echo.
    echo 3. 📱 CONNECT LIVE: Open Ableton Live
    echo    → Enable "Link/Tempo/MIDI" sync
    echo    → UDP port 8000 for real-time integration
    echo    → Create amazing Max for Live devices!
    
    set SETUP_COMPLETE=1
) else (
    echo 1. 📥 INSTALL NODE.JS:
    echo    → Download from: https://nodejs.org
    echo    → Choose LTS version (18 or higher^)
    echo    → Follow installation wizard
    echo    → Restart computer after installation
    echo.
    echo 2. 🔄 RUN SETUP AGAIN:
    echo    → Double-click this setup script again
    echo    → Verify all requirements are met
    echo.
    echo 3. 🚀 LAUNCH DEVIBLE:
    echo    → Use LAUNCH_DEVIBLE.bat after setup complete
)

echo.
echo =============================================================================

if %SETUP_COMPLETE% EQU 1 (
    echo [SUCCESS] 🎉 Setup complete! Devible is ready to launch.
    echo.
    echo Would you like to start Devible now?
    choice /c YN /m "Start Devible now (Y/N)?"
    if !errorlevel! equ 1 (
        echo.
        echo [INFO] 🚀 Starting Devible...
        call LAUNCH_DEVIBLE.bat
    )
) else (
    echo [INCOMPLETE] ⚠️ Setup incomplete. Please install missing requirements.
)

echo.
echo [INFO] This setup window will close in 30 seconds...
echo [INFO] Re-run anytime to check requirements or start Devible.
timeout /t 30
exit /b 0
