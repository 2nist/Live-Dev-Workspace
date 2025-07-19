# ALSE Platform - Windows PowerShell Start Script
Write-Host "🚀 Starting ALSE Development Platform..." -ForegroundColor Green

# Check prerequisites
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is required but not installed" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is required but not installed" -ForegroundColor Red
    exit 1
}

# Create necessary directories
$directories = @(
    "data\patches",
    "data\templates", 
    "data\ai-models",
    "data\test-results",
    "logs",
    "monitoring\prometheus",
    "monitoring\grafana\dashboards",
    "monitoring\grafana\datasources",
    "monitoring\logstash\pipeline",
    "monitoring\logstash\config"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "📁 Created directory: $dir" -ForegroundColor Cyan
    }
}

# Generate environment file if not exists
if (-not (Test-Path ".env")) {
    $jwtSecret = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes([System.Guid]::NewGuid().ToString()))
    @"
JWT_SECRET=$jwtSecret
AUDIO_DEVICE_ID=default
NODE_ENV=development
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "🔑 Generated environment configuration" -ForegroundColor Yellow
}

# Start development services
Write-Host "🐳 Starting Docker services..." -ForegroundColor Blue
docker-compose up -d postgres redis elasticsearch

# Wait for databases
Write-Host "⏳ Waiting for databases to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Start application services
docker-compose up -d

Write-Host "✅ Platform started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔌 API Gateway: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 Monitoring: http://localhost:3001 (admin/admin)" -ForegroundColor Cyan
Write-Host "🔍 Kibana: http://localhost:5601" -ForegroundColor Cyan
Write-Host "📈 Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "💾 MinIO: http://localhost:9001" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Logs: docker-compose logs -f [service-name]" -ForegroundColor Gray
Write-Host "🛑 Stop: docker-compose down" -ForegroundColor Gray
