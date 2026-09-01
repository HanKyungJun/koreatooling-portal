# ============================================================
#  cnc-wiki  Windows Task Scheduler setup  (rev 2026-08-28)
#
#  ASCII ONLY - do not add Korean text to this file.
#  Reason: Windows PowerShell 5.1 writes CP949 by default; the
#  previous setup_scheduler.ps1 embedded a Korean filename in the
#  OnBoot task and it was stored mangled ('_?????.xlsx'), so the
#  "run only if today's report is missing" check ALWAYS failed and
#  the task re-ran on every boot.
#
#  Changes vs setup_scheduler.ps1:
#   1. CNC_Daily_Report now runs daily_and_upload.bat, which also
#      does generate.py (portal build + GitHub Pages push).
#   2. The separate 17:00 "cnc-wiki Netlify upload" task is removed.
#      It was missed ~62% of the time (25 of last 40 runs fired the
#      next morning because the PC was off at 17:00).
#   3. OnBoot check uses a date-prefix wildcard instead of the Korean
#      filename, so no encoding dependency.
#
#  Run in an ADMINISTRATOR PowerShell:
#     powershell -ExecutionPolicy Bypass -File scripts\setup_scheduler_v2.ps1
# ============================================================

$ErrorActionPreference = 'Stop'

$Base = "C:\Users\TOOLKOREA\Desktop\cnc-wiki"
$Bat  = "$Base\scripts\daily_and_upload.bat"
$Dir  = "$Base\wiki\reports\daily"
$User = "$env:USERDOMAIN\$env:USERNAME"

if (-not (Test-Path $Bat)) { throw "not found: $Bat" }

$Principal = New-ScheduledTaskPrincipal -UserId $User -LogonType S4U -RunLevel Highest

# ---- 1) main daily task : report + calendar + overview + portal push ----
$A1 = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$Bat`"" -WorkingDirectory $Base
$T1 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "16:00"
$S1 = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun `
        -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "CNC_Daily_Report" -Action $A1 -Trigger $T1 `
        -Settings $S1 -Principal $Principal `
        -Description "Daily report + calendar + overview + portal upload (16:00 weekdays)" -Force | Out-Null
Write-Host "[OK] CNC_Daily_Report        -> daily_and_upload.bat @ 16:00 Mon-Fri"

# ---- 2) on-boot catch-up : ASCII-safe existence check ----
$Check = "`$d = Get-Date -Format 'yyyy-MM-dd'; " +
         "`$hit = Get-ChildItem -LiteralPath '$Dir' -Filter (`$d + '*.xlsx') -ErrorAction SilentlyContinue; " +
         "if (-not `$hit) { cmd.exe /c '$Bat' }"
$A2 = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -NonInteractive -ExecutionPolicy Bypass -Command `"$Check`"" `
        -WorkingDirectory $Base
$T2 = New-ScheduledTaskTrigger -AtStartup
$S2 = New-ScheduledTaskSettingsSet -StartWhenAvailable `
        -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "CNC_Daily_Report_OnBoot" -Action $A2 -Trigger $T2 `
        -Settings $S2 -Principal $Principal `
        -Description "Catch-up run at boot when today's report is missing (date-prefix check)" -Force | Out-Null
Write-Host "[OK] CNC_Daily_Report_OnBoot -> date-prefix check (no Korean, encoding-safe)"

# ---- 3) remove the old separate 17:00 upload task ----
$old = Get-ScheduledTask | Where-Object { $_.TaskName -like 'cnc-wiki Netlify*' }
if ($old) {
    foreach ($t in $old) {
        Unregister-ScheduledTask -TaskName $t.TaskName -Confirm:$false
        Write-Host "[OK] removed old task      -> $($t.TaskName)"
    }
} else {
    Write-Host "[--] no 'cnc-wiki Netlify*' task found (already removed?)"
}

Write-Host ""
Write-Host "Done. Verify:"
Write-Host "  Get-ScheduledTask -TaskName 'CNC_*' | Format-List TaskName,State"
Write-Host "  Get-ScheduledTask | ? { `$_.TaskName -like 'cnc-wiki*' } | Select TaskName"
Write-Host ""
Write-Host "Test without waiting for 16:00:"
Write-Host "  Start-ScheduledTask -TaskName 'CNC_Daily_Report'"
