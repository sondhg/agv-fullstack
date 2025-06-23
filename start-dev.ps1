# AGV Fullstack Development Startup Script
# This script starts all required services for local development in the background

Write-Host "Starting AGV Fullstack Development Environment..." -ForegroundColor Green

# Global variables to store process IDs
$global:ProcessIds = @{}
$global:LogDir = "logs"

# Create logs directory if it doesn't exist
if (-not (Test-Path $global:LogDir)) {
    New-Item -ItemType Directory -Path $global:LogDir | Out-Null
}

# Function to start a service in the background
function Start-ServiceInBackground {
    param(
        [string]$Title,
        [string]$Command,
        [string]$WorkingDirectory = $PWD,
        [string]$LogFile,
        [int]$Port = 0
    )
    
    Write-Host "Starting $Title..." -ForegroundColor Yellow
    
    $process = Start-Process powershell -ArgumentList "-WindowStyle", "Hidden", "-Command", $Command -WorkingDirectory $WorkingDirectory -PassThru -RedirectStandardOutput "$global:LogDir\$LogFile" -RedirectStandardError "$global:LogDir\$LogFile.error"
    $global:ProcessIds[$Title] = @{
        "ProcessId" = $process.Id
        "Port" = $Port
        "LogFile" = $LogFile
    }
    
    # Wait a moment to check if process started successfully
    Start-Sleep -Milliseconds 500
    if ($process.HasExited) {
        Write-Host "Failed to start $Title" -ForegroundColor Red
        return $false
    } else {
        Write-Host "$Title started successfully (PID: $($process.Id))" -ForegroundColor Green
        return $true
    }
}

# Function to save process IDs to file
function Save-ProcessIds {
    $global:ProcessIds | ConvertTo-Json | Out-File "dev-processes.json"
}

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Virtual environment not found. Please create one first with 'python -m venv .venv'" -ForegroundColor Red
    exit 1
}

# Check if Docker is running (for Redis)
try {
    docker version | Out-Null
    Write-Host "Docker is available" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running or not installed. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if mosquitto is available
try {
    mosquitto --help | Out-Null
    Write-Host "Mosquitto is available" -ForegroundColor Green
} catch {
    Write-Host "Mosquitto is not installed or not in PATH. Please install Mosquitto MQTT broker." -ForegroundColor Red
    exit 1
}

Write-Host "`nStarting services in background..." -ForegroundColor Cyan

# Start Redis server
$redisStarted = Start-ServiceInBackground -Title "Redis Server" -Command "docker run --rm -p 6379:6379 redis:7" -LogFile "redis.log" -Port 6379

# Start Mosquitto MQTT broker
$mosquittoStarted = Start-ServiceInBackground -Title "Mosquitto MQTT Broker" -Command "mosquitto -v" -LogFile "mosquitto.log" -Port 1883

# Wait for Redis and Mosquitto to start
if ($redisStarted -and $mosquittoStarted) {
    Write-Host "Waiting for Redis and Mosquitto to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3

    # Start Django server
    $djangoCommand = "Set-Location 'agv_server'; & '..\\.venv\\Scripts\\Activate.ps1'; python manage.py runserver"
    $djangoStarted = Start-ServiceInBackground -Title "Django Server" -Command $djangoCommand -LogFile "django.log" -Port 8000

    # Start React frontend
    $reactCommand = "Set-Location 'frontend'; pnpm run dev"
    $reactStarted = Start-ServiceInBackground -Title "React Frontend" -Command $reactCommand -LogFile "react.log" -Port 5173

    if ($djangoStarted -and $reactStarted) {
        # Save process IDs for shutdown script
        Save-ProcessIds
        
        Write-Host "`nAll services are running in background!" -ForegroundColor Green
        Write-Host "Services started:" -ForegroundColor Cyan
        Write-Host "- Redis Server (Docker container on port 6379)" -ForegroundColor White
        Write-Host "- Mosquitto MQTT Broker" -ForegroundColor White
        Write-Host "- Django Server (usually on http://127.0.0.1:8000/)" -ForegroundColor White
        Write-Host "- React Frontend (usually on http://localhost:5173/)" -ForegroundColor White
        Write-Host "`nLogs are being written to the 'logs' directory" -ForegroundColor Yellow
        Write-Host "To stop all services, run: .\stop-dev.ps1" -ForegroundColor Yellow
        Write-Host "To view logs in real-time, run: .\view-logs.ps1 -Service <service-name>" -ForegroundColor Yellow
    } else {
        Write-Host "Failed to start some services. Check logs in the 'logs' directory." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Failed to start Redis or Mosquitto. Cannot continue." -ForegroundColor Red
    exit 1
}
