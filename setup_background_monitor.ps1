# Background Monitor Setup - PowerShell Script
# ==============================================
# Sets up persistent background monitoring for Ghost funds

# Configuration
$PYTHON_PATH = "venv\Scripts\python"
$SCRIPT_PATH = "ghost_sentry_loop.py"
$LOG_FILE = "sentry_log.txt"
$INTERVAL_SECONDS = 300  # 5 minutes

# Create log file
if (!(Test-Path $LOG_FILE)) {
    New-Item -ItemType File -Path $LOG_FILE -Force
}

# Function to run the sentry loop
function Start-SentryLoop {
    param(
        [string]$LogFile = $LOG_FILE
    )
    
    while ($true) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        
        try {
            Write-Output "$timestamp - Starting Ghost Sentry Loop..." | Out-File -Append $LogFile
            
            # Run the Python script
            & $PYTHON_PATH $SCRIPT_PATH 2>&1 | Out-File -Append $LogFile
            
            $result = $LASTEXITCODE
            
            if ($result -eq 0) {
                Write-Output "$timestamp - Sentry completed successfully" | Out-File -Append $LogFile
                break  # Exit if recovery was successful
            }
            else {
                Write-Output "$timestamp - Sentry continuing, next check in $INTERVAL_SECONDS seconds" | Out-File -Append $LogFile
            }
        }
        catch {
            Write-Output "$timestamp - ERROR: $_" | Out-File -Append $LogFile
        }
        
        Start-Sleep -Seconds $INTERVAL_SECONDS
    }
}

# Start the background process
Write-Host "🚀 Starting Ghost Sentry Background Monitor..." -ForegroundColor Green
Write-Host "📋 Log file: $LOG_FILE" -ForegroundColor Cyan
Write-Host "⏰ Poll interval: $INTERVAL_SECONDS seconds" -ForegroundColor Cyan
Write-Host "🎯 Monitoring for $15 ETH recovery..." -ForegroundColor Yellow

# Start in background
$job = Start-Job -ScriptBlock {
    param($PythonPath, $ScriptPath, $LogFile, $Interval)
    
    & $using:PythonPath $using:ScriptPath
    
} -ArgumentList $PYTHON_PATH, $SCRIPT_PATH, $LOG_FILE, $INTERVAL_SECONDS

Write-Host "✅ Background monitor started (Job ID: $($job.Id))" -ForegroundColor Green
Write-Host "📊 Check status with: Get-Job $($job.Id)" -ForegroundColor Cyan
Write-Host "📋 View logs with: Get-Content $LOG_FILE" -ForegroundColor Cyan
Write-Host "🛑 Stop with: Stop-Job $($job.Id)" -ForegroundColor Red

# Optional: Show real-time log tail
Write-Host "`n📋 Real-time logs (Ctrl+C to stop):" -ForegroundColor Yellow
try {
    Get-Content $LOG_FILE -Tail 0 -Wait
}
catch {
    # User pressed Ctrl+C
}

# Cleanup on exit
if ($job.State -eq "Running") {
    Stop-Job $job.Id
    Remove-Job $job.Id
}
