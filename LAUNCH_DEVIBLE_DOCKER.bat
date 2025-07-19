@echo off
REM =============================================================================
REM Devible - One-Click Docker Launch for Windows
REM Professional Max for Live IDE with Docker
REM =============================================================================

echo.
echo  ████████╗ ███████╗ ██╗   ██╗ ██╗ ██████╗  ██╗     ███████╗
echo  ██╔══██║ ██╔════╝ ██║   ██║ ██║ ██╔══██╗ ██║     ██╔════╝
echo  ██║  ██║ █████╗   ██║   ██║ ██║ ██████╔╝ ██║     █████╗
echo  ██║  ██║ ██╔══╝   ╚██╗ ██╔╝ ██║ ██╔══██╗ ██║     ██╔══╝
echo  ██████╔╝ ███████╗  ╚████╔╝  ██║ ██████╔╝ ███████╗███████╗
echo  ╚═════╝  ╚══════╝   ╚═══╝   ╚═╝ ╚═════╝  ╚══════╝╚══════╝
echo.
echo  Professional Max for Live IDE - v2.0 Beta (Docker Edition)
echo  One-Click Launch with Docker
echo.

REM Check if Docker is installed and running
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker not found!
    echo.
    echo Please install Docker Desktop from: https://docker.com/products/docker-desktop
    echo.
    echo After installation:
    echo 1. Start Docker Desktop
    echo 2. Wait for it to be "running"
    echo 3. Restart this script
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop and wait for it to be ready.
    echo You should see "Docker Desktop is running" in the system tray.
    echo.
    echo Then restart this script.
    pause
    exit /b 1
)

echo [INFO] ✅ Docker is ready!
echo.

REM Navigate to project directory
cd /d "%~dp0"

REM Check if docker-compose.devible.yml exists
if not exist "docker-compose.devible.yml" (
    echo [ERROR] docker-compose.devible.yml not found!
    echo [ERROR] Please ensure you're running this from the correct directory.
    pause
    exit /b 1
)

REM Stop any existing containers
echo [INFO] 🔄 Stopping any existing Devible containers...
docker-compose -f docker-compose.devible.yml down --remove-orphans >nul 2>&1

REM Build and start containers
echo [INFO] 🚀 Building and starting Devible...
echo [INFO] This may take a few minutes on first run...
echo.

docker-compose -f docker-compose.devible.yml up --build -d

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start Devible containers!
    echo.
    echo Please check Docker Desktop and try again.
    pause
    exit /b 1
)

REM Wait for services to be ready
echo [INFO] ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if Devible is responding
curl -f http://localhost:3000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] ⏳ Still starting up... Please wait...
    timeout /t 15 /nobreak >nul
)

echo.
echo [SUCCESS] ✅ Devible is now running!
echo.
echo 🌐 Web Interface:     http://localhost:3000
echo 💾 Storage Console:   http://localhost:9001
echo 📊 Redis Monitoring:  http://localhost:6379
echo.
echo [INFO] Opening browser...
start "" "http://localhost:3000"

echo.
echo [INFO] Devible is running in Docker containers.
echo [INFO] Your patches and templates are safely stored in Docker volumes.
echo.
echo [INFO] To stop Devible, close this window or press Ctrl+C
echo [INFO] To restart later, just run this script again!
echo.

REM Show container status
echo [INFO] Container Status:
docker-compose -f docker-compose.devible.yml ps

echo.
echo [INFO] Press Ctrl+C to stop Devible, or close this window.
echo [INFO] Logs will appear below:
echo.

REM Follow logs
docker-compose -f docker-compose.devible.yml logs -f

REM If we get here, user pressed Ctrl+C
echo.
echo [INFO] Stopping Devible...
docker-compose -f docker-compose.devible.yml down
echo [INFO] ✅ Devible stopped successfully!
echo [INFO] Thanks for using Devible! 🎵✨
pause
