$base = "C:\Users\TOOLKOREA\Desktop\cnc-wiki\바로가기"
$desk = [Environment]::GetFolderPath("Desktop")
$ws   = New-Object -COM WScript.Shell

# ① 포털 시작
$s = $ws.CreateShortcut("$desk\① 포털 시작.lnk")
$s.TargetPath       = "$base\①_포털_시작.bat"
$s.WorkingDirectory = "C:\Users\TOOLKOREA\Desktop\cnc-wiki"
$s.IconLocation     = "$env:SystemRoot\System32\shell32.dll,23"
$s.Save()

# ③ 현장기록 시트
$s = $ws.CreateShortcut("$desk\③ 현장기록 시트.lnk")
$s.TargetPath   = "$base\③_현장기록_시트.url"
$s.IconLocation = "$env:SystemRoot\System32\shell32.dll,14"
$s.Save()

Write-Host "완료: 바탕화면에 바로가기 2개 생성됨" -ForegroundColor Green
