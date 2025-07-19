# =============================================================================
# Devible - Professional Max for Live IDE
# PowerShell Launch Script for Windows
# =============================================================================

# Set execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# ASCII Art Header
Write-Host ""
Write-Host "  ████████╗ ███████╗ ██╗   ██╗ ██╗ ██████╗  ██╗     ███████╗" -ForegroundColor Magenta
Write-Host "  ██╔══██║ ██╔════╝ ██║   ██║ ██║ ██╔══██╗ ██║     ██╔════╝" -ForegroundColor Magenta
Write-Host "  ██║  ██║ █████╗   ██║   ██║ ██║ ██████╔╝ ██║     █████╗" -ForegroundColor Magenta
Write-Host "  ██║  ██║ ██╔══╝   ╚██╗ ██╔╝ ██║ ██╔══██╗ ██║     ██╔══╝" -ForegroundColor Magenta
Write-Host "  ██████╔╝ ███████╗  ╚████╔╝  ██║ ██████╔╝ ███████╗███████╗" -ForegroundColor Magenta
Write-Host "  ╚═════╝  ╚══════╝   ╚═══╝   ╚═╝ ╚═════╝  ╚══════╝╚══════╝" -ForegroundColor Magenta
Write-Host ""
Write-Host "  Professional Max for Live IDE - v2.0 Beta" -ForegroundColor Blue
Write-Host "  The Future of Visual Music Programming" -ForegroundColor Blue
Write-Host ""

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check if Node.js is installed
if (-not (Test-Command "node")) {
    Write-Host "[ERROR] Node.js not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Node.js 18+ from: https://nodejs.org" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installation, restart this script." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js version
Write-Host "[INFO] Checking Node.js version..." -ForegroundColor Blue
$nodeVersion = node -v
Write-Host "[INFO] Node.js version: $nodeVersion" -ForegroundColor Blue

# Navigate to project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptPath\max-live-ide"

# Check if package.json exists
if (-not (Test-Path "package.json")) {
    Write-Host "[ERROR] package.json not found!" -ForegroundColor Red
    Write-Host "[ERROR] Please ensure you're running this from the correct directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies if node_modules doesn't exist
if (-not (Test-Path "node_modules")) {
    Write-Host ""
    Write-Host "[INFO] Installing dependencies... This may take a few minutes." -ForegroundColor Yellow
    Write-Host "[INFO] ⏳ Setting up Devible for first-time use..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[SUCCESS] ✅ Dependencies installed successfully!" -ForegroundColor Green
}

# Start the development server
Write-Host ""
Write-Host "[INFO] 🚀 Starting Devible..." -ForegroundColor Green
Write-Host "[INFO] Opening browser at http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "[INFO] Ready to create amazing Max for Live devices!" -ForegroundColor Green
Write-Host "[INFO] Press Ctrl+C to stop the server when done." -ForegroundColor Green
Write-Host ""

# Open browser after a short delay
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:3000"
} | Out-Null

# Start the React development server
npm start

# If we get here, the server was stopped
Write-Host ""
Write-Host "[INFO] Devible server stopped." -ForegroundColor Blue
Write-Host "[INFO] Thanks for using Devible! 🎵✨" -ForegroundColor Blue
Read-Host "Press Enter to exit"
