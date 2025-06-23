# AGV Fullstack Development Log Viewer
# This script helps you view logs from the development services

param(
    [string]$Service = "",
    [switch]$List,
    [switch]$All
)

$LogDir = "logs"

function Show-Usage {
    Write-Host "AGV Development Log Viewer" -ForegroundColor Green
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\view-logs.ps1 -List                    # List available log files"
    Write-Host "  .\view-logs.ps1 -Service <name>          # View specific service log"
    Write-Host "  .\view-logs.ps1 -All                     # View all logs in separate windows"
    Write-Host ""
    Write-Host "Available services: redis, mosquitto, django, react" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\view-logs.ps1 -Service django          # View Django logs"
    Write-Host "  .\view-logs.ps1 -List                    # Show all log files"
}

if (-not (Test-Path $LogDir)) {
    Write-Host "Logs directory not found. Make sure you've started the development environment first." -ForegroundColor Red
    exit 1
}

if ($List) {
    Write-Host "Available log files:" -ForegroundColor Green
    Get-ChildItem $LogDir -Filter "*.log" | ForEach-Object {
        $size = [math]::Round($_.Length / 1KB, 2)
        Write-Host "  $($_.Name) (${size}KB)" -ForegroundColor White
    }
    
    $errorFiles = Get-ChildItem $LogDir -Filter "*.error"
    if ($errorFiles) {
        Write-Host "`nError files:" -ForegroundColor Red
        $errorFiles | ForEach-Object {
            $size = [math]::Round($_.Length / 1KB, 2)
            Write-Host "  $($_.Name) (${size}KB)" -ForegroundColor White
        }
    }
    exit 0
}

if ($All) {
    Write-Host "Opening all log files in separate windows..." -ForegroundColor Green
    Get-ChildItem $LogDir -Filter "*.log" | ForEach-Object {
        $logPath = $_.FullName
        $title = $_.BaseName
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'Viewing $title logs - Press Ctrl+C to exit' -ForegroundColor Green; Get-Content '$logPath' -Wait"
    }
    exit 0
}

if ($Service -eq "") {
    Show-Usage
    exit 0
}

$logFile = Join-Path $LogDir "$Service.log"
$errorFile = Join-Path $LogDir "$Service.log.error"

if (-not (Test-Path $logFile)) {
    Write-Host "Log file not found: $logFile" -ForegroundColor Red
    Write-Host "Available services: " -NoNewline -ForegroundColor Yellow
    Get-ChildItem $LogDir -Filter "*.log" | ForEach-Object { 
        Write-Host $_.BaseName -NoNewline -ForegroundColor White
        Write-Host ", " -NoNewline
    }
    Write-Host ""
    exit 1
}

Write-Host "Viewing $Service logs (Press Ctrl+C to exit)" -ForegroundColor Green
Write-Host "Log file: $logFile" -ForegroundColor Gray

if ((Test-Path $errorFile) -and (Get-Item $errorFile).Length -gt 0) {
    Write-Host "Warning: Error file exists and is not empty: $errorFile" -ForegroundColor Red
}

Write-Host "----------------------------------------" -ForegroundColor Gray

try {
    Get-Content $logFile -Wait
} catch {
    Write-Host "Error reading log file: $($_.Exception.Message)" -ForegroundColor Red
}
