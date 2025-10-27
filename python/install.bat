@echo off
REM Installation script for live-dev-integration (Windows)

echo === Live Dev Integration Setup ===
echo.

REM Check Python version
echo Checking Python version...
python --version

REM Check if we're in the right directory
if not exist "setup.py" (
    echo Error: Please run this script from the python\ directory
    exit /b 1
)

REM Create virtual environment (optional)
set /p VENV="Create virtual environment? (recommended) [y/N] "
if /i "%VENV%"=="y" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Virtual environment created and activated
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install package in development mode
echo Installing live-dev-integration...
pip install -e .

echo.
echo Installation complete!
echo.
echo Next steps:
echo   1. Make sure AbletonOSC is installed in Ableton Live
echo   2. Start Ableton Live and enable AbletonOSC in Preferences
echo   3. Try running an example:
echo      cd examples
echo      python 01_basic_connection.py
echo.

REM Offer to run test
set /p TEST="Test connection now? (requires Live to be running) [y/N] "
if /i "%TEST%"=="y" (
    echo Testing connection...
    python -c "from live_dev import LiveConnection; LiveConnection().test_connection()"
)

echo.
echo Setup complete!
pause
