# Max Live IDE Start Script
Set-Location "C:\Users\CraftAuto-Sales\OneDrive\Documents\ALSE\max-live-ide"
$env:FORCE_COLOR = "1"
$env:BROWSER = "none"

Write-Host "Starting Max Live IDE..." -ForegroundColor Green
Write-Host "Directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host "Package.json exists: $(Test-Path './package.json')" -ForegroundColor Yellow

# Try different approaches
try {
    Write-Host "Attempting to start React development server..." -ForegroundColor Cyan
    & node ".\node_modules\react-scripts\bin\react-scripts.js" start
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Trying alternative method..." -ForegroundColor Yellow
    npm start
}
