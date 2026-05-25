Set fso = CreateObject("Scripting.FileSystemObject")
Set ws = CreateObject("WScript.Shell")
projectDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = fso.BuildPath(ws.ExpandEnvironmentStrings("%USERPROFILE%"), "python\pythonw.exe")
pyw = fso.BuildPath(projectDir, "run.pyw")
ws.Run """" & pythonw & """ """ & pyw & """", 0, False
