# AGV Fullstack Development Shutdown Script
# This script gracefully stops all development services in the correct order

Write-Host "Stopping AGV Fullstack Development Environment..." -ForegroundColor Red

# Function to kill processes by port
function Stop-ProcessByPort {
    param(
        [int]$Port,
        [string]$ServiceName
    )
    
    Write-Host "Stopping $ServiceName on port $Port..." -ForegroundColor Yellow
    
    try {
        # Find processes using the port
        $netstatOutput = netstat -ano | Select-String ":$Port\s"
        if ($netstatOutput) {
            foreach ($line in $netstatOutput) {
                if ($line -match '\s+(\d+)$') {
                    $pid = $matches[1]
                    try {
                        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                        if ($process) {
                            Write-Host "  Killing process $($process.ProcessName) (PID: $pid)" -ForegroundColor Gray
                            Stop-Process -Id $pid -Force
                        }
                    } catch {
                        Write-Host "  Failed to stop process $pid" -ForegroundColor Red
                    }
                }
            }
            Write-Host "$ServiceName stopped successfully" -ForegroundColor Green        } else {
            Write-Host "$ServiceName was not running on port $Port" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Failed to stop ${ServiceName}: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to stop process tree
function Stop-ProcessTree {
    param(
        [int]$ProcessId,
        [string]$Title
    )
    
    Write-Host "Stopping $Title and its child processes (PID: $ProcessId)..." -ForegroundColor Yellow
    
    try {
        # Get all child processes
        $childProcesses = Get-WmiObject -Class Win32_Process -Filter "ParentProcessId=$ProcessId" -ErrorAction SilentlyContinue
        
        # Stop child processes first
        foreach ($child in $childProcesses) {
            try {
                Write-Host "  Stopping child process $($child.Name) (PID: $($child.ProcessId))" -ForegroundColor Gray
                Stop-Process -Id $child.ProcessId -Force -ErrorAction SilentlyContinue
            } catch {
                # Ignore errors for child processes that might already be stopped
            }
        }
        
        # Stop the main process
        $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $ProcessId -Force
            Write-Host "$Title stopped successfully" -ForegroundColor Green        } else {
            Write-Host "$Title was not running" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Failed to stop ${Title}: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to stop Docker containers
function Stop-DockerContainers {
    Write-Host "Stopping Docker containers..." -ForegroundColor Yellow
    try {
        # Stop Redis container
        $containers = docker ps --filter "ancestor=redis:7" --format "{{.ID}}" 2>$null
        if ($containers) {
            foreach ($container in $containers) {
                Write-Host "  Stopping Redis container: $container" -ForegroundColor Gray
                docker stop $container 2>$null | Out-Null
            }
            Write-Host "Redis Docker containers stopped" -ForegroundColor Green        } else {
            Write-Host "No Redis containers running" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Failed to stop Docker containers: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to stop processes by name pattern
function Stop-ProcessByName {
    param(
        [string]$ProcessName,
        [string]$ServiceName
    )
    
    Write-Host "Stopping $ServiceName processes..." -ForegroundColor Yellow
    try {
        $processes = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
        if ($processes) {
            foreach ($proc in $processes) {
                Write-Host "  Stopping $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Gray
                Stop-Process -Id $proc.Id -Force
            }
            Write-Host "$ServiceName processes stopped" -ForegroundColor Green        } else {
            Write-Host "No $ServiceName processes found" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Failed to stop ${ServiceName}: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "Stopping services in correct order..." -ForegroundColor Cyan

# Stop React Frontend (port 5173)
Stop-ProcessByPort -Port 5173 -ServiceName "React Frontend"
Start-Sleep -Seconds 1

# Stop Django Server (port 8000)
Stop-ProcessByPort -Port 8000 -ServiceName "Django Server"
Start-Sleep -Seconds 1

# Stop any remaining Node.js processes (React dev server)
Stop-ProcessByName -ProcessName "node" -ServiceName "Node.js (React)"

# Stop any remaining Python processes (Django)
$pythonProcesses = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "Stopping Python processes..." -ForegroundColor Yellow
    foreach ($proc in $pythonProcesses) {
        # Check if it's likely our Django process by looking at command line
        try {
            $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            if ($commandLine -and ($commandLine.Contains("manage.py") -or $commandLine.Contains("runserver"))) {
                Write-Host "  Stopping Django process (PID: $($proc.Id))" -ForegroundColor Gray
                Stop-Process -Id $proc.Id -Force
            }
        } catch {
            # If we can't get command line, stop it anyway if it's in our project directory
            Write-Host "  Stopping Python process (PID: $($proc.Id))" -ForegroundColor Gray
            Stop-Process -Id $proc.Id -Force
        }
    }
}

# Stop Mosquitto
Stop-ProcessByName -ProcessName "mosquitto" -ServiceName "Mosquitto MQTT Broker"

# Stop Redis Docker containers
Stop-DockerContainers

# If process tracking file exists, try to clean up tracked processes
if (Test-Path "dev-processes.json") {
    try {
        $processData = Get-Content "dev-processes.json" | ConvertFrom-Json
        Write-Host "Cleaning up tracked processes..." -ForegroundColor Yellow
        
        $processData.PSObject.Properties | ForEach-Object {
            $serviceName = $_.Name
            $serviceInfo = $_.Value
            
            if ($serviceInfo.ProcessId) {
                try {
                    $process = Get-Process -Id $serviceInfo.ProcessId -ErrorAction SilentlyContinue
                    if ($process) {
                        Write-Host "  Force stopping tracked $serviceName (PID: $($serviceInfo.ProcessId))" -ForegroundColor Gray
                        Stop-Process -Id $serviceInfo.ProcessId -Force
                    }
                } catch {
                    # Process likely already stopped
                }
            }
        }
    } catch {
        Write-Host "Could not read process tracking file" -ForegroundColor Yellow
    }
    
    # Clean up process file
    Remove-Item "dev-processes.json" -ErrorAction SilentlyContinue
    Write-Host "Cleaned up process tracking file" -ForegroundColor Green
}

Write-Host "`nAll development services have been stopped!" -ForegroundColor Green
Write-Host "Logs are preserved in the 'logs' directory for review" -ForegroundColor Yellow

# Final verification
Start-Sleep -Seconds 2
Write-Host "`nVerifying services are stopped..." -ForegroundColor Cyan

$ports = @(5173, 8000, 6379, 1883)
$stillRunning = @()

foreach ($port in $ports) {
    $netstatOutput = netstat -ano | Select-String ":$port\s"
    if ($netstatOutput) {
        $stillRunning += $port
    }
}

if ($stillRunning.Count -gt 0) {
    Write-Host "Warning: Some services may still be running on ports: $($stillRunning -join ', ')" -ForegroundColor Yellow
    Write-Host "You may need to manually stop them or restart your computer" -ForegroundColor Yellow
} else {
    Write-Host "All services verified stopped!" -ForegroundColor Green
}
