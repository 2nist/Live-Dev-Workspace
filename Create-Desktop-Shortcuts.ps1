# =============================================================================
# Create Desktop Shortcuts for Devible
# PowerShell script to create convenient desktop shortcuts
# =============================================================================

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Creating shortcuts (no admin required)..." -ForegroundColor Blue
}

# Get current script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopPath = [Environment]::GetFolderPath("Desktop")

# Create WScript shell object
$WshShell = New-Object -comObject WScript.Shell

Write-Host ""
Write-Host "🚀 Creating Devible Desktop Shortcuts..." -ForegroundColor Green
Write-Host ""

# Shortcut 1: Quick Launch
$shortcut1 = $WshShell.CreateShortcut("$desktopPath\🎛️ Launch Devible.lnk")
$shortcut1.TargetPath = "$scriptPath\LAUNCH_DEVIBLE.bat"
$shortcut1.WorkingDirectory = $scriptPath
$shortcut1.Description = "Devible - Professional Max for Live IDE"
$shortcut1.IconLocation = "shell32.dll,22"  # Music note icon
$shortcut1.Save()
Write-Host "✅ Created: 🎛️ Launch Devible.lnk" -ForegroundColor Green

# Shortcut 2: Docker Launch
if (Test-Path "$scriptPath\LAUNCH_DEVIBLE_DOCKER.bat") {
    $shortcut2 = $WshShell.CreateShortcut("$desktopPath\🐳 Launch Devible (Docker).lnk")
    $shortcut2.TargetPath = "$scriptPath\LAUNCH_DEVIBLE_DOCKER.bat"
    $shortcut2.WorkingDirectory = $scriptPath
    $shortcut2.Description = "Devible - Docker Containerized Launch"
    $shortcut2.IconLocation = "shell32.dll,44"  # Container icon
    $shortcut2.Save()
    Write-Host "✅ Created: 🐳 Launch Devible (Docker).lnk" -ForegroundColor Green
}

# Shortcut 3: Setup
if (Test-Path "$scriptPath\SETUP_DEVIBLE.bat") {
    $shortcut3 = $WshShell.CreateShortcut("$desktopPath\⚙️ Setup Devible.lnk")
    $shortcut3.TargetPath = "$scriptPath\SETUP_DEVIBLE.bat"
    $shortcut3.WorkingDirectory = $scriptPath
    $shortcut3.Description = "Devible - Setup and Requirements Check"
    $shortcut3.IconLocation = "shell32.dll,16"  # Settings icon
    $shortcut3.Save()
    Write-Host "✅ Created: ⚙️ Setup Devible.lnk" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Desktop shortcuts created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now launch Devible directly from your desktop:" -ForegroundColor Blue
Write-Host "• 🎛️ Launch Devible - Quick development start" -ForegroundColor White
Write-Host "• 🐳 Launch Devible (Docker) - Containerized deployment" -ForegroundColor White
Write-Host "• ⚙️ Setup Devible - Check requirements and setup" -ForegroundColor White
Write-Host ""
Write-Host "Ready to create amazing Max for Live devices! 🎵✨" -ForegroundColor Magenta

Read-Host "Press Enter to exit"
