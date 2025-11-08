# User-level automation setup (no admin required)
# This creates scheduled tasks for the current user only

$projectPath = "C:\AI Projects\Document Controller"
$pythonExe = "$projectPath\.venv\Scripts\python.exe"

Write-Host "Setting up User-Level AI Document Controller Automation..." -ForegroundColor Green
Write-Host "NOTE: These tasks run only when you are logged in." -ForegroundColor Yellow
Write-Host ""

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
    # Create user-level scheduled tasks
    Write-Host "Creating user-level scheduled tasks..." -ForegroundColor Yellow
    
    # Daily task
    $dailyAction = New-ScheduledTaskAction -Execute $pythonExe -Argument "$projectPath\automation_launcher.py daily" -WorkingDirectory $projectPath
    $dailyTrigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"
    $dailySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    Register-ScheduledTask -TaskName "AI Document Controller - Daily Cleanup (User)" -Action $dailyAction -Trigger $dailyTrigger -Settings $dailySettings -Description "Daily document cleanup and duplicate detection (User level)" -Force
    
    # Weekly task
    $weeklyAction = New-ScheduledTaskAction -Execute $pythonExe -Argument "$projectPath\automation_launcher.py weekly" -WorkingDirectory $projectPath
    $weeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "3:00AM"
    $weeklySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    Register-ScheduledTask -TaskName "AI Document Controller - Weekly Organization (User)" -Action $weeklyAction -Trigger $weeklyTrigger -Settings $weeklySettings -Description "Weekly file organization and management (User level)" -Force
    
    # Monthly task 
    $monthlyAction = New-ScheduledTaskAction -Execute $pythonExe -Argument "$projectPath\automation_launcher.py monthly" -WorkingDirectory $projectPath
    $monthlyTrigger = New-ScheduledTaskTrigger -Once -At "4:00AM"
    $monthlyTrigger.Repetition = $(New-ScheduledTaskTrigger -Once -At "4:00AM" -RepetitionInterval (New-TimeSpan -Days 30)).Repetition
    $monthlySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    Register-ScheduledTask -TaskName "AI Document Controller - Monthly Analysis (User)" -Action $monthlyAction -Trigger $monthlyTrigger -Settings $monthlySettings -Description "Monthly deep file analysis and optimization (User level)" -Force
    
    Write-Host "SUCCESS: User-level automation tasks created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Created Tasks:" -ForegroundColor Cyan
    Write-Host "   - Daily Cleanup (User) - Every day at 2:00 AM"
    Write-Host "   - Weekly Organization (User) - Every Sunday at 3:00 AM"  
    Write-Host "   - Monthly Analysis (User) - 1st of every month at 4:00 AM"
    Write-Host ""
    Write-Host "IMPORTANT: These tasks only run when you are logged in." -ForegroundColor Yellow
    Write-Host "For system-level tasks, run the main setup script as Administrator." -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host "ERROR creating user-level tasks: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "You can still run automation manually:" -ForegroundColor Yellow
    Write-Host "   python automation_launcher.py daily" -ForegroundColor White
    Write-Host "   python automation_launcher.py weekly" -ForegroundColor White
    Write-Host "   python automation_launcher.py monthly" -ForegroundColor White
}

Write-Host ""
Write-Host "To manage your tasks:" -ForegroundColor Yellow
Write-Host "   - Open Task Scheduler (taskschd.msc)"
Write-Host "   - Look in Task Scheduler Library for 'AI Document Controller' tasks"
Write-Host "   - Right-click to run, disable, or modify"
Write-Host ""
Write-Host "To test automation manually:" -ForegroundColor Yellow
Write-Host "   python automation_launcher.py daily"
Write-Host "   python automation_launcher.py weekly" 
Write-Host "   python automation_launcher.py monthly"
Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green