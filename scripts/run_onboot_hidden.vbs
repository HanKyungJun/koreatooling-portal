Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\TOOLKOREA\Desktop\cnc-wiki"
rc = sh.Run("""powershell.exe"" -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command ""$d = Get-Date -Format 'yyyy-MM-dd'; $hit = Get-ChildItem -LiteralPath 'C:\Users\TOOLKOREA\Desktop\cnc-wiki\wiki\reports\daily' -Filter ($d + '*.xlsx') -ErrorAction SilentlyContinue; if (-not $hit) { cmd.exe /c 'C:\Users\TOOLKOREA\Desktop\cnc-wiki\scripts\daily_and_upload.bat' }""", 0, True)
WScript.Quit rc
