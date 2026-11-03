# test_step5_rc.ps1  (2026-10-14, Cowork)  -- ASCII only, keep it that way.
# 1) Re-checks the step 5 return-code logic of scripts\daily_and_upload.bat
#    in a temp folder (real logs are not touched). Three cases:
#      A  python exits 0, log free      -> expect rc=0
#      B  python exits 3, log free      -> expect rc=3
#      C  python exits 0, log LOCKED    -> expect rc=1 + [step5-fail] dump
#    Case C reproduces the 10-14 morning error ("being used by another process").
# 2) Probes the real generate.log right now (HELD/FREE) and lists python processes.
# Run from the cnc-wiki folder:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\test_step5_rc.ps1
# If any case FAILs, restore:  copy scripts\daily_and_upload.bat.bak_20261014 scripts\daily_and_upload.bat

$root = Split-Path -Parent $PSScriptRoot
$bat  = Join-Path $root 'scripts\daily_and_upload.bat'
$lines = @(Get-Content -LiteralPath $bat)
$i0 = -1; $i1 = -1
for ($k = 0; $k -lt $lines.Count; $k++) {
  if ($i0 -lt 0 -and $lines[$k].StartsWith('echo [step5-start]')) { $i0 = $k }
  if ($lines[$k].StartsWith('exit /b %RC5%')) { $i1 = $k }
}
if ($i0 -lt 0 -or $i1 -le $i0) { Write-Output 'FAIL: step5 block not found in daily_and_upload.bat'; exit 2 }

$tmp = Join-Path $env:TEMP ('step5test_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
New-Item -ItemType Directory -Path $tmp | Out-Null
$fake = 'python -c "import sys,os; sys.exit(int(os.environ[''TESTRC'']))"'
$body = foreach ($ln in $lines[$i0..$i1]) {
  $ln.Replace('python generate.py', $fake).Replace('wiki\reports\daily\', ($tmp + '\'))
}
$testBat = Join-Path $tmp 'step5test.bat'
Set-Content -LiteralPath $testBat -Encoding ASCII -Value (@('@echo off') + $body)

function Run-Case([string]$name, [int]$rc, [bool]$lock, [int]$expect) {
  foreach ($f in 'run.log','step5_err.log','generate.log') {
    $p = Join-Path $tmp $f
    if (Test-Path -LiteralPath $p) { Clear-Content -LiteralPath $p }
  }
  $env:TESTRC = "$rc"
  $fs = $null
  if ($lock) { $fs = [System.IO.File]::Open((Join-Path $tmp 'generate.log'), 'OpenOrCreate', 'Write', 'Read') }
  & cmd.exe /c $testBat | Out-Null
  $exitCode = $LASTEXITCODE
  if ($fs) { $fs.Close() }
  $runLog = ''
  if (Test-Path -LiteralPath (Join-Path $tmp 'run.log')) { $runLog = Get-Content -LiteralPath (Join-Path $tmp 'run.log') -Raw }
  $logged = 'none'
  if ($runLog -match 'step5-end\].*rc=(\S+)') { $logged = $Matches[1] }
  $err = ''
  if (Test-Path -LiteralPath (Join-Path $tmp 'step5_err.log')) { $err = Get-Content -LiteralPath (Join-Path $tmp 'step5_err.log') -Raw }
  $ok = ($exitCode -eq $expect) -and ($logged -eq "$expect")
  if ($lock) { $ok = $ok -and ($err -match 'step5-fail') -and ($err -match 'ProcessId') }
  $tag = 'FAIL'
  if ($ok) { $tag = 'PASS' }
  Write-Host ("{0}  case {1}: exit={2} logged rc={3} expect={4}" -f $tag, $name, $exitCode, $logged, $expect)
  if ($lock) {
    $first = ($err -split "`r?`n" | Where-Object { $_ -ne '' } | Select-Object -First 2) -join ' | '
    Write-Host ("      step5_err.log first lines: {0}" -f $first)
  }
  return $ok
}

$r = @()
$r += Run-Case 'A' 0 $false 0
$r += Run-Case 'B' 3 $false 3
$r += Run-Case 'C' 0 $true  1
Remove-Item Env:\TESTRC -ErrorAction SilentlyContinue
if ($r -contains $false) { Write-Output 'RESULT: SOME FAIL - restore the backup (see header)' } else { Write-Output 'RESULT: ALL PASS' }
Write-Output ("temp folder (not deleted): {0}" -f $tmp)

Write-Output ''
Write-Output '--- probe: real generate.log right now ---'
$real = Join-Path $root 'wiki\reports\daily\generate.log'
try {
  $h = [System.IO.File]::Open($real, 'Open', 'Write', 'Read')
  $h.Close()
  Write-Output 'generate.log: FREE (nobody holds it for writing now)'
} catch {
  Write-Output ('generate.log: HELD - ' + $_.Exception.InnerException.Message + $_.Exception.Message)
}
Write-Output '--- python processes now ---'
Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python' } |
  Select-Object ProcessId, ParentProcessId, CreationDate, CommandLine | Format-List | Out-String -Width 300
