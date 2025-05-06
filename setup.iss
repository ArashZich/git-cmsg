[Setup]
AppName=Git-CMSG
AppVersion=0.1.0
DefaultDirName={autopf}\Git-CMSG
DefaultGroupName=Git-CMSG
OutputBaseFilename=git-cmsg-0.1.0-setup
Compression=lzma
SolidCompression=yes
ChangesEnvironment=yes

[Files]
Source: "dist\git_cmsg.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Git-CMSG"; Filename: "{app}\git_cmsg.exe"
Name: "{group}\Uninstall Git-CMSG"; Filename: "{uninstallexe}"

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath(ExpandConstant('{app}'))

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKLM, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;