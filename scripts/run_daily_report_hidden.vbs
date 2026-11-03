Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\TOOLKOREA\Desktop\cnc-wiki"
rc = sh.Run("""cmd.exe"" /c ""C:\Users\TOOLKOREA\Desktop\cnc-wiki\scripts\daily_and_upload.bat""", 0, True)
WScript.Quit rc
