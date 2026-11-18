# Weekly sales board task: every Wednesday 09:00 (PC local time = KST).
# Runs "erp\sales_board.py --weekly" -> base date = last Tuesday, writes Excel to
# private_local\sales_board\<excel folder>, then opens it on screen. 2026-11-18, Cowork.
# ERP is reachable only from this PC, so this is a Windows task (not a cloud task).
# ASCII only - no Korean text in this file.
#
#   powershell -ExecutionPolicy Bypass -File scripts\register_sales_weekly_task.ps1          (show plan only)
#   powershell -ExecutionPolicy Bypass -File scripts\register_sales_weekly_task.ps1 -Apply   (register)
#   Undo: Unregister-ScheduledTask -TaskName CNC_Sales_Weekly -Confirm:$false
param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$Name = 'CNC_Sales_Weekly'
$Repo = Split-Path -Parent $PSScriptRoot
$Args0 = 'erp\sales_board.py --weekly'

$py = $null
$cmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
if ($cmd) { $py = $cmd.Source }
if (-not $py) {
    $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $cand = Join-Path (Split-Path -Parent $cmd.Source) 'pythonw.exe'
        if (Test-Path $cand) { $py = $cand } else { $py = $cmd.Source }
    }
}
if (-not $py) { Write-Host 'STOP: python not found'; exit 1 }

Write-Host "Task    : $Name"
Write-Host "Run     : $py $Args0"
Write-Host "Folder  : $Repo"
Write-Host 'When    : every Wednesday 09:00, run later if the PC was off (StartWhenAvailable)'
Write-Host 'Session : only when logged on (Interactive) - needed to open Excel on screen'
if (-not $Apply) { Write-Host 'Plan only. Add -Apply to register.'; exit 0 }

$action    = New-ScheduledTaskAction -Execute $py -Argument $Args0 -WorkingDirectory $Repo
$trigger   = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Wednesday -At '09:00'
$settings  = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $Name -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null

$t = Get-ScheduledTask -TaskName $Name
$a = $t.Actions[0]
$i = Get-ScheduledTaskInfo -TaskName $Name
Write-Host "Check   : Execute=$($a.Execute)"
Write-Host "Check   : Arguments=$($a.Arguments)  WorkingDirectory=$($a.WorkingDirectory)"
Write-Host "Check   : NextRunTime=$($i.NextRunTime)"
if ($a.Arguments -ne $Args0 -or $a.WorkingDirectory -ne $Repo) { Write-Host 'NOT APPLIED'; exit 1 }
Write-Host 'APPLIED'
