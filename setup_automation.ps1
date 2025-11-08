# PowerShell script to set up Windows Task Scheduler for Document Controller Automation
# Run this as Administrator

$projectPath = "C:\AI Projects\Document Controller"
$pythonExe = "$projectPath\.venv\Scripts\python.exe"

Write-Host "Setting up AI Document Controller Automation Tasks..." -ForegroundColor Green

# Check if project exists
if (-not (Test-Path $projectPath)) {
    Write-Host "ERROR: Project not found at $projectPath" -ForegroundColor Red
    exit 1
}

# Check if Python executable exists
if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Python executable not found at $pythonExe" -ForegroundColor Red
    exit 1
}

try {
    # Daily Cleanup Task
    Write-Host "Creating daily cleanup task..." -ForegroundColor Yellow
    $dailyAction = New-ScheduledTaskAction -Execute $pythonExe -Argument "$projectPath\automation_launcher.py daily" -WorkingDirectory $projectPath
    $dailyTrigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"
    $dailySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $dailyPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U
    
    Register-ScheduledTask -TaskName "AI Document Controller - Daily Cleanup" -Action $dailyAction -Trigger $dailyTrigger -Settings $dailySettings -Principal $dailyPrincipal -Description "Daily document cleanup and duplicate detection" -Force
    
    # Weekly Organization Task
    Write-Host "Creating weekly organization task..." -ForegroundColor Yellow
    $weeklyAction = New-ScheduledTaskAction -Execute $pythonExe -Argument "$projectPath\automation_launcher.py weekly" -WorkingDirectory $projectPath
    $weeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "3:00AM"
    $weeklySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $weeklyPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U
    
    Register-ScheduledTask -TaskName "AI Document Controller - Weekly Organization" -Action $weeklyAction -Trigger $weeklyTrigger -Settings $weeklySettings -Principal $weeklyPrincipal -Description "Weekly file organization and management" -Force
    
    # Monthly Deep Analysis Task
    Write-Host "Creating monthly analysis task..." -ForegroundColor Yellow
    $monthlyAction = New-ScheduledTaskAction -Execute $pythonExe -Argument "$projectPath\automation_launcher.py monthly" -WorkingDirectory $projectPath
    $monthlyTrigger = New-ScheduledTaskTrigger -Once -At "4:00AM"
    $monthlyTrigger.Repetition = $(New-ScheduledTaskTrigger -Once -At "4:00AM" -RepetitionInterval (New-TimeSpan -Days 30)).Repetition
    $monthlySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $monthlyPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U
    
    Register-ScheduledTask -TaskName "AI Document Controller - Monthly Analysis" -Action $monthlyAction -Trigger $monthlyTrigger -Settings $monthlySettings -Principal $monthlyPrincipal -Description "Monthly deep file analysis and optimization" -Force
    
    Write-Host "SUCCESS: Automation tasks created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Created Tasks:" -ForegroundColor Cyan
    Write-Host "   - Daily Cleanup - Every day at 2:00 AM"
    Write-Host "   - Weekly Organization - Every Sunday at 3:00 AM"
    Write-Host "   - Monthly Analysis - 1st of every month at 4:00 AM"
    Write-Host ""
    Write-Host "To manage tasks:" -ForegroundColor Yellow
    Write-Host "   - Open Task Scheduler (taskschd.msc)"
    Write-Host "   - Look for 'AI Document Controller' tasks"
    Write-Host "   - Right-click to run, disable, or modify"
    Write-Host ""
    Write-Host "To test automation:" -ForegroundColor Yellow
    Write-Host "   python automation_launcher.py daily"
    Write-Host "   python automation_launcher.py weekly"
    Write-Host "   python automation_launcher.py monthly"
    Write-Host ""
    
} catch {
    Write-Host "ERROR creating scheduled tasks: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "TIP: Try running PowerShell as Administrator" -ForegroundColor Yellow
}

# Display current configuration
Write-Host "Current Configuration:" -ForegroundColor Cyan
$envPath = "$projectPath\.env"
if (Test-Path $envPath) {
    $config = Get-Content $envPath | Where-Object { $_ -match "^[A-Z_]+=.*" -and $_ -notmatch "^#" }
    foreach ($line in $config) {
        if ($line -match "^(DAILY_AUTOMATION|WEEKLY_AUTOMATION|MONTHLY_AUTOMATION|AUTO_.*|OLD_FILE_THRESHOLD_DAYS)=(.*)") {
            Write-Host "   $($Matches[1]): $($Matches[2])" -ForegroundColor White
        }
    }
} else {
    Write-Host "   WARNING: Configuration file not found: $envPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete! Your documents will now be automatically managed." -ForegroundColor Green