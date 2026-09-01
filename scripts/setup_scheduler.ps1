# CNC Daily Report - Windows Task Scheduler Setup
# Run as Administrator in PowerShell

$TaskName  = "CNC_Daily_Report"
$TaskName2 = "CNC_Daily_Report_OnBoot"
$BaseDir   = "C:\Users\TOOLKOREA\Desktop\cnc-wiki"
$LogFile   = "$BaseDir\wiki\reports\daily\run.log"
$RunTime   = "16:00"

# --- Task 1: Weekdays (Mon-Fri) at 16:00 ---
# NOTE: 3 python steps chained with "&" (not "&&") on purpose -
#       calendar updates must still run even if daily_report.py fails/exits non-zero.

$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c cd /d `"$BaseDir`" && python scripts\daily_report.py >> `"$LogFile`" 2>&1 & python scripts\update_calendar_artifact.py >> `"$LogFile`" 2>&1 & python scripts\update_calendar_claude_work.py >> `"$LogFile`" 2>&1" `
    -WorkingDirectory $BaseDir

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At $RunTime

$Settings = New-ScheduledTaskSettingsSet `
    -WakeToRun `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Regrinding daily report + calendar update, weekdays at $RunTime" `
    -Force

Write-Host ""
Write-Host "=========================================="
Write-Host " Task 1 registered: $TaskName"
Write-Host " Schedule: Weekdays (Mon-Fri) at $RunTime"
Write-Host " Output: $BaseDir\wiki\reports\daily\"
Write-Host "=========================================="

# --- Task 2: On boot (generate today's report if missing) ---

$CheckScript = "cd '$BaseDir'; `$f='$BaseDir\wiki\reports\daily\' + (Get-Date -Format 'yyyy-MM-dd') + '_일일보고.xlsx'; if(-not(Test-Path `$f)){python scripts\daily_report.py >> '$LogFile' 2>&1; python scripts\update_calendar_artifact.py >> '$LogFile' 2>&1; python scripts\update_calendar_claude_work.py >> '$LogFile' 2>&1}"

$Action2 = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -NonInteractive -Command `"$CheckScript`"" `
    -WorkingDirectory $BaseDir

$Trigger2 = New-ScheduledTaskTrigger -AtStartup

$Settings2 = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask `
    -TaskName $TaskName2 `
    -Action $Action2 `
    -Trigger $Trigger2 `
    -Settings $Settings2 `
    -Principal $Principal `
    -Description "Generate daily report on PC boot if missing" `
    -Force

Write-Host ""
Write-Host "Task 2 registered: $TaskName2 (runs on PC startup)"
Write-Host ""
Write-Host "[NOTE] Sleep/Hibernate: WakeToRun enabled - will wake PC automatically"
Write-Host "[NOTE] Full Shutdown:   Task 2 will run report on next PC startup"
Write-Host ""
Write-Host "To verify: taskschd.msc  or  Get-ScheduledTask -TaskName 'CNC_*'"

# --- Task 3: Daily 단가 0 출하 전표 알림 (09:00) ---

$TaskName3  = "DailyZeroPriceAlert"
$ERPDir     = "$BaseDir\erp"
$ZeroLog    = "$ERPDir\zero_price_alert.log"
$AlertTime  = "09:00"

$Action3 = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c cd /d `"$ERPDir`" && python zero_price_alert.py >> `"$ZeroLog`" 2>&1" `
    -WorkingDirectory $ERPDir

$Trigger3 = New-ScheduledTaskTrigger -Daily -At $AlertTime

$Settings3 = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask `
    -TaskName $TaskName3 `
    -Action $Action3 `
    -Trigger $Trigger3 `
    -Settings $Settings3 `
    -Principal $Principal `
    -Description "Daily zero-price shipment alert via Gmail at 09:00" `
    -Force

Write-Host ""
Write-Host "Task 3 registered: $TaskName3 (runs daily at $AlertTime)"
Write-Host " Log: $ZeroLog"
