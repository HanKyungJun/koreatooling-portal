# hide_onboot_task_window.ps1  (2026-10-12)
# Purpose : run the CNC_Daily_Report_OnBoot (logon catch-up) task with NO console window,
#           same method as hide_daily_task_window.ps1 (16:00 task, verified 2026-10-12
#           LastTaskResult 0). Closing the window / Ctrl+C can no longer kill the morning run.
# How     : the task's current command line (powershell "run only if today's xlsx is
#           missing" check) is wrapped UNCHANGED in a VBS launcher
#           (WScript.Shell.Run ..., 0 = hidden, True = wait) and the action is switched
#           to wscript.exe. Trigger (AtLogOn + Delay PT3M) / user / logon type are NOT changed.
# Usage   : (admin PowerShell, in the cnc-wiki folder)
#             .\scripts\hide_onboot_task_window.ps1           -> show only (no change)
#             .\scripts\hide_onboot_task_window.ps1 -Apply    -> backup + apply
# Rollback: Register-ScheduledTask -TaskName CNC_Daily_Report_OnBoot -Xml (Get-Content outputs\CNC_Daily_Report_OnBoot_backup_20261012.xml -Raw) -Force
# NOTE    : ASCII only on purpose (Windows PowerShell 5.1 reads BOM-less files as CP949).

param([switch]$Apply, [string]$TaskName = "CNC_Daily_Report_OnBoot")

$BaseDir = "C:\Users\TOOLKOREA\Desktop\cnc-wiki"
$Vbs     = Join-Path $BaseDir "scripts\run_onboot_hidden.vbs"
$Backup  = Join-Path $BaseDir "outputs\CNC_Daily_Report_OnBoot_backup_20261012.xml"

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
$act  = $task.Actions | Select-Object -First 1
Write-Host "== current =="
Write-Host ("Execute   : " + $act.Execute)
Write-Host ("Arguments : " + $act.Arguments)
Write-Host ("LogonType : " + $task.Principal.LogonType + " / RunLevel: " + $task.Principal.RunLevel)
foreach ($t in $task.Triggers) { Write-Host ("Trigger   : " + $t.CimClass.CimClassName + " Delay=" + $t.Delay) }

if ($act.Execute -match 'wscript') {
    Write-Host "Already wscript - nothing to do."
    return
}

$cmdLine = '"' + $act.Execute + '" ' + $act.Arguments
$vbsBody = @(
    'Set sh = CreateObject("WScript.Shell")'
    ('sh.CurrentDirectory = "' + $BaseDir + '"')
    ('rc = sh.Run("' + $cmdLine.Replace('"', '""') + '", 0, True)')
    'WScript.Quit rc'
) -join "`r`n"

Write-Host ""
Write-Host "== new (planned) =="
Write-Host ("Execute   : wscript.exe")
Write-Host ("Arguments : //B //Nologo `"" + $Vbs + "`"")
Write-Host "VBS       :"
Write-Host $vbsBody

if (-not $Apply) {
    Write-Host ""
    Write-Host "Dry run only. Re-run with -Apply to change the task."
    return
}

New-Item -ItemType Directory -Force -Path (Split-Path $Backup) | Out-Null
Export-ScheduledTask -TaskName $TaskName | Out-File -FilePath $Backup -Encoding Unicode
Set-Content -Path $Vbs -Value $vbsBody -Encoding ASCII
$newAct = New-ScheduledTaskAction -Execute "wscript.exe" -Argument ("//B //Nologo `"" + $Vbs + "`"") -WorkingDirectory $BaseDir
try {
    Set-ScheduledTask -TaskName $TaskName -Action $newAct -ErrorAction Stop | Out-Null
} catch {
    Write-Host ""
    Write-Host ("FAILED: " + $_.Exception.Message)
    Write-Host "Run this in an ADMINISTRATOR PowerShell (right-click PowerShell > Run as administrator)."
    exit 1
}

# 2026-10-08: verify instead of assuming (an access-denied run once printed APPLIED)
$chk = (Get-ScheduledTask -TaskName $TaskName).Actions | Select-Object -First 1
Write-Host ""
if ($chk.Execute -match 'wscript') {
    Write-Host ("APPLIED. Execute=" + $chk.Execute + "  Arguments=" + $chk.Arguments)
} else {
    Write-Host ("NOT APPLIED - task still runs: " + $chk.Execute + " " + $chk.Arguments)
    exit 1
}
foreach ($t in (Get-ScheduledTask -TaskName $TaskName).Triggers) { Write-Host ("Trigger   : " + $t.CimClass.CimClassName + " Delay=" + $t.Delay) }
Write-Host ("Backup : " + $Backup)
