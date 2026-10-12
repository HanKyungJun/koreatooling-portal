# delay_onboot_trigger.ps1  (2026-10-12)
# Purpose : delay the CNC_Daily_Report_OnBoot logon trigger by 3 minutes so it no longer
#           starts at the same moment as the Startup-folder cnc-wiki-generate.bat.
#           Both run generate.py; on 2026-10-12 morning generate ran twice in a row
#           (07:56 / 07:57) and could fight over .git/index.lock.
# How     : sets Delay = PT3M on every logon trigger of the task. Action, condition,
#           user and logon type are NOT changed.
# Usage   : (ADMIN PowerShell, in the cnc-wiki folder)
#             .\scripts\delay_onboot_trigger.ps1          -> show only (no change)
#             .\scripts\delay_onboot_trigger.ps1 -Apply   -> backup + apply + verify
# Rollback: Register-ScheduledTask -TaskName CNC_Daily_Report_OnBoot -Xml (Get-Content outputs\CNC_Daily_Report_OnBoot_backup_20261012.xml -Raw) -Force
# NOTE    : ASCII only on purpose (Windows PowerShell 5.1 reads BOM-less files as CP949).
param([switch]$Apply, [string]$TaskName = "CNC_Daily_Report_OnBoot", [string]$Delay = "PT3M")

$BaseDir = "C:\Users\TOOLKOREA\Desktop\cnc-wiki"
$Backup  = Join-Path $BaseDir "outputs\CNC_Daily_Report_OnBoot_backup_20261012.xml"

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
Write-Host "== current =="
$i = 0
foreach ($t in $task.Triggers) {
    $i++
    Write-Host ("Trigger " + $i + " : " + $t.CimClass.CimClassName + "  Delay=" + $t.Delay + "  Enabled=" + $t.Enabled)
}
Write-Host ("LogonType : " + $task.Principal.LogonType + " / RunLevel: " + $task.Principal.RunLevel)

$logon = @($task.Triggers | Where-Object { $_.CimClass.CimClassName -eq 'MSFT_TaskLogonTrigger' })
if ($logon.Count -eq 0) {
    Write-Host "No logon trigger found - nothing changed. (Expected AtLogOn since 2026-09-10.)"
    exit 1
}
if (@($logon | Where-Object { $_.Delay -ne $Delay }).Count -eq 0) {
    Write-Host ("Already Delay=" + $Delay + " - nothing to do.")
    return
}

Write-Host ""
Write-Host ("== planned == logon trigger Delay -> " + $Delay)

if (-not $Apply) {
    Write-Host ""
    Write-Host "Dry run only. Re-run with -Apply to change the task."
    return
}

New-Item -ItemType Directory -Force -Path (Split-Path $Backup) | Out-Null
Export-ScheduledTask -TaskName $TaskName | Out-File -FilePath $Backup -Encoding Unicode
foreach ($t in $task.Triggers) {
    if ($t.CimClass.CimClassName -eq 'MSFT_TaskLogonTrigger') { $t.Delay = $Delay }
}
try {
    Set-ScheduledTask -TaskName $TaskName -Trigger $task.Triggers -ErrorAction Stop | Out-Null
} catch {
    Write-Host ""
    Write-Host ("FAILED: " + $_.Exception.Message)
    Write-Host "Run this in an ADMINISTRATOR PowerShell (right-click PowerShell > Run as administrator)."
    exit 1
}

# verify by reading back (an access-denied run once printed APPLIED - 2026-10-08)
$chk = Get-ScheduledTask -TaskName $TaskName
$bad = @($chk.Triggers | Where-Object { $_.CimClass.CimClassName -eq 'MSFT_TaskLogonTrigger' -and $_.Delay -ne $Delay })
$act = $chk.Actions | Select-Object -First 1
Write-Host ""
if ($bad.Count -eq 0) {
    Write-Host ("APPLIED. logon trigger Delay=" + $Delay + "  (action unchanged: " + $act.Execute + ")")
} else {
    Write-Host "NOT APPLIED - logon trigger delay is still different. Nothing else was changed."
    exit 1
}
Write-Host ("Backup : " + $Backup)
