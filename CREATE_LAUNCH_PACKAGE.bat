@echo off
REM =============================================================================
REM Devible - All-in-One Package Installer
REM Creates a complete executable launch package
REM =============================================================================

echo.
echo  ████████╗ ███████╗ ██╗   ██╗ ██╗ ██████╗  ██╗     ███████╗
echo  ██╔══██║ ██╔════╝ ██║   ██║ ██║ ██╔══██╗ ██║     ██╔════╝
echo  ██║  ██║ █████╗   ██║   ██║ ██║ ██████╔╝ ██║     █████╗
echo  ██║  ██║ ██╔══╝   ╚██╗ ██╔╝ ██║ ██╔══██╗ ██║     ██╔══╝
echo  ██████╔╝ ███████╗  ╚████╔╝  ██║ ██████╔╝ ███████╗███████╗
echo  ╚═════╝  ╚══════╝   ╚═══╝   ╚═╝ ╚═════╝  ╚══════╝╚══════╝
echo.
echo  Package Installer - Creating Executable Launch Package
echo.

set PACKAGE_DIR=devible-launch-package
set CURRENT_DIR=%CD%

echo [INFO] 📦 Creating Devible Launch Package...
echo.

REM Create package directory
if exist "%PACKAGE_DIR%" (
    echo [INFO] Cleaning existing package directory...
    rmdir /s /q "%PACKAGE_DIR%"
)

mkdir "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%\launchers"
mkdir "%PACKAGE_DIR%\docker"
mkdir "%PACKAGE_DIR%\docs"

echo [INFO] ✅ Package directory structure created
echo.

REM Copy launcher scripts
echo [INFO] 📋 Copying launcher scripts...
copy "LAUNCH_DEVIBLE.bat" "%PACKAGE_DIR%\" >nul
copy "launch-devible.sh" "%PACKAGE_DIR%\" >nul
copy "Launch-Devible.ps1" "%PACKAGE_DIR%\launchers\" >nul
copy "LAUNCH_DEVIBLE_DOCKER.bat" "%PACKAGE_DIR%\" >nul
copy "SETUP_DEVIBLE.bat" "%PACKAGE_DIR%\" >nul

REM Copy Docker files
echo [INFO] 🐳 Copying Docker configuration...
copy "docker-compose.devible.yml" "%PACKAGE_DIR%\docker\" >nul
if exist "max-live-ide\Dockerfile" copy "max-live-ide\Dockerfile" "%PACKAGE_DIR%\docker\" >nul
if exist "max-live-ide\nginx.conf" copy "max-live-ide\nginx.conf" "%PACKAGE_DIR%\docker\" >nul

REM Copy documentation
echo [INFO] 📚 Copying documentation...
copy "LAUNCH_GUIDE.md" "%PACKAGE_DIR%\docs\" >nul
if exist "max-live-ide\README.md" copy "max-live-ide\README.md" "%PACKAGE_DIR%\docs\" >nul
if exist "max-live-ide\BETA_TESTING_PLAN.md" copy "max-live-ide\BETA_TESTING_PLAN.md" "%PACKAGE_DIR%\docs\" >nul

REM Copy desktop shortcut creator
copy "Create-Desktop-Shortcuts.ps1" "%PACKAGE_DIR%\" >nul

REM Create main package launcher
echo [INFO] 🚀 Creating main package launcher...

(
echo @echo off
echo REM Devible Launch Package - Main Launcher
echo.
echo echo.
echo echo  ████████╗ ███████╗ ██╗   ██╗ ██╗ ██████╗  ██╗     ███████╗
echo echo  ██╔══██║ ██╔════╝ ██║   ██║ ██║ ██╔══██╗ ██║     ██╔════╝
echo echo  ██║  ██║ █████╗   ██║   ██║ ██║ ██████╔╝ ██║     █████╗
echo echo  ██║  ██║ ██╔══╝   ╚██╗ ██╔╝ ██║ ██╔══██╗ ██║     ██╔══╝
echo echo  ██████╔╝ ███████╗  ╚████╔╝  ██║ ██████╔╝ ███████╗███████╗
echo echo  ╚═════╝  ╚══════╝   ╚═══╝   ╚═╝ ╚═════╝  ╚══════╝╚══════╝
echo echo.
echo echo  Professional Max for Live IDE - Launch Package
echo echo  Choose your preferred launch method:
echo echo.
echo echo  1. Quick Setup ^& Launch ^(Recommended^)
echo echo  2. Direct Launch ^(Node.js Development^)
echo echo  3. Docker Launch ^(Containerized^)
echo echo  4. Create Desktop Shortcuts
echo echo  5. View Documentation
echo echo  6. Exit
echo echo.
echo choice /c 123456 /m "Select option (1-6): "
echo.
echo if errorlevel 6 exit /b 0
echo if errorlevel 5 start "" "docs\LAUNCH_GUIDE.md" ^& goto menu
echo if errorlevel 4 powershell -ExecutionPolicy Bypass -File "Create-Desktop-Shortcuts.ps1" ^& goto menu
echo if errorlevel 3 call "LAUNCH_DEVIBLE_DOCKER.bat"
echo if errorlevel 2 call "LAUNCH_DEVIBLE.bat"
echo if errorlevel 1 call "SETUP_DEVIBLE.bat"
echo.
echo :menu
echo echo.
echo echo Press any key to return to menu...
echo pause ^>nul
echo goto start
echo.
echo :start
echo cls
echo goto menu
) > "%PACKAGE_DIR%\START_DEVIBLE.bat"

REM Create README for package
echo [INFO] 📝 Creating package README...

(
echo # 🚀 Devible Launch Package
echo.
echo **Easy Executable Launch Package for Devible - Professional Max for Live IDE**
echo.
echo ## Quick Start
echo.
echo 1. **Double-click `START_DEVIBLE.bat`** for interactive launcher
echo 2. **Choose your preferred option:**
echo    - Quick Setup ^& Launch ^(checks requirements first^)
echo    - Direct Launch ^(for development^)
echo    - Docker Launch ^(for production^)
echo.
echo ## Package Contents
echo.
echo - `START_DEVIBLE.bat` - Interactive main launcher
echo - `SETUP_DEVIBLE.bat` - Requirements checker and setup
echo - `LAUNCH_DEVIBLE.bat` - Direct Node.js development launch
echo - `LAUNCH_DEVIBLE_DOCKER.bat` - Docker containerized launch
echo - `Create-Desktop-Shortcuts.ps1` - Desktop shortcut creator
echo - `docs/` - Complete documentation
echo - `docker/` - Docker deployment files
echo - `launchers/` - Additional launcher scripts
echo.
echo ## System Requirements
echo.
echo - **Node.js 18+** ^(for direct launch^)
echo - **Docker Desktop** ^(for containerized launch^)
echo - **4GB RAM minimum**, 8GB recommended
echo - **Windows 10/11**, macOS 10.15+, or Ubuntu 18.04+
echo.
echo ## Support
echo.
echo - View `docs/LAUNCH_GUIDE.md` for detailed instructions
echo - Check `docs/BETA_TESTING_PLAN.md` for testing information
echo - Visit Discord: discord.gg/devible
echo.
echo **Ready to create amazing Max for Live devices! 🎵✨**
) > "%PACKAGE_DIR%\README.md"

REM Create portable batch launcher for macOS/Linux
echo [INFO] 🍎 Creating cross-platform launcher...

(
echo #!/bin/bash
echo # Devible Launch Package - Cross-Platform Launcher
echo.
echo echo ""
echo echo "  ████████╗ ███████╗ ██╗   ██╗ ██╗ ██████╗  ██╗     ███████╗"
echo echo "  ██╔══██║ ██╔════╝ ██║   ██║ ██║ ██╔══██╗ ██║     ██╔════╝"
echo echo "  ██║  ██║ █████╗   ██║   ██║ ██║ ██████╔╝ ██║     █████╗"
echo echo "  ██║  ██║ ██╔══╝   ╚██╗ ██╔╝ ██║ ██╔══██╗ ██║     ██╔══╝"
echo echo "  ██████╔╝ ███████╗  ╚████╔╝  ██║ ██████╔╝ ███████╗███████╗"
echo echo "  ╚═════╝  ╚══════╝   ╚═══╝   ╚═╝ ╚═════╝  ╚══════╝╚══════╝"
echo echo ""
echo echo "  Professional Max for Live IDE - Launch Package"
echo echo ""
echo.
echo echo "Choose launch method:"
echo echo "1. Direct Launch (Node.js Development)"
echo echo "2. Docker Launch (Containerized)"
echo echo "3. View Documentation"
echo echo "4. Exit"
echo echo ""
echo.
echo read -p "Select option (1-4): " choice
echo.
echo case $choice in
echo     1^) ./launch-devible.sh ;;
echo     2^) docker-compose -f docker/docker-compose.devible.yml up --build -d ;;
echo     3^) open docs/LAUNCH_GUIDE.md 2^>/dev/null ^|^| xdg-open docs/LAUNCH_GUIDE.md 2^>/dev/null ;;
echo     4^) exit 0 ;;
echo     *^) echo "Invalid option" ;;
echo esac
) > "%PACKAGE_DIR%\start-devible.sh"

echo [INFO] ✅ Package creation complete!
echo.

REM Make shell script executable (if on Windows with WSL)
where wsl >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    wsl chmod +x "%PACKAGE_DIR%/start-devible.sh" 2>nul
    wsl chmod +x "%PACKAGE_DIR%/launch-devible.sh" 2>nul
)

echo =============================================================================
echo  📦 DEVIBLE LAUNCH PACKAGE CREATED
echo =============================================================================
echo.
echo Package Location: %CURRENT_DIR%\%PACKAGE_DIR%
echo Package Size: 
for /f "tokens=3" %%i in ('dir "%PACKAGE_DIR%" ^| find "File(s)"') do echo    %%i bytes
echo.
echo 🚀 **Ready to Use:**
echo    → Double-click "%PACKAGE_DIR%\START_DEVIBLE.bat"
echo    → Interactive launcher with all options
echo.
echo 📱 **Cross-Platform:**
echo    → Windows: START_DEVIBLE.bat
echo    → macOS/Linux: start-devible.sh
echo.
echo 📦 **Portable:**
echo    → Copy entire folder to any computer
echo    → No installation required
echo    → All dependencies included
echo.
echo 🎵 **Ready to create amazing Max for Live devices!**
echo.

choice /c YN /m "Would you like to test the package now (Y/N)?"
if %errorlevel% equ 1 (
    echo.
    echo [INFO] 🧪 Testing package...
    cd "%PACKAGE_DIR%"
    call "START_DEVIBLE.bat"
)

echo.
echo [SUCCESS] ✅ Devible Launch Package ready for distribution!
echo [INFO] Package can be zipped and shared with users.
pause
exit /b 0
