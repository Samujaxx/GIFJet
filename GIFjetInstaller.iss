[Setup]
AppName=GIFjet
AppVersion=1.0
DefaultDirName={autopf}\GIFjet
DefaultGroupName=GIFjet
UninstallDisplayIcon={app}\GIFjet.exe
OutputDir=Installer
OutputBaseFilename=GIFjetSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardResizable=yes
UsePreviousAppDir=no
SetupIconFile=assets\setupicon.ico
WizardImageFile=assets\header.bmp
WizardSmallImageFile=assets\icon.bmp

[Files]
; Adjust paths to assets, config, and other files relative to the installer script location
Source: "src\dist\main.exe"; DestDir: "{app}"; DestName: "GIFJet.exe"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs
Source: "src\style.qss"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
Name: "autostart"; Description: "Start GIFjet with Windows"; GroupDescription: "Startup options:"
Name: "runafterinstall"; Description: "Launch GIFjet after installation"; GroupDescription: "Installation options:"

[Icons]
Name: "{group}\GIFjet"; Filename: "{app}\GIFJet.exe"
Name: "{commondesktop}\GIFjet"; Filename: "{app}\GIFJet.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "GIFjet"; \
    ValueData: """{app}\GIFjet.exe"""; Flags: uninsdeletevalue; Tasks: autostart

[Code]
var
  RunAfterInstall: Boolean;
  ResultCode: Integer;  // Declare the ResultCode variable

procedure InitializeWizard;
begin
  // Set the default value of the "runafterinstall" checkbox to true
  RunAfterInstall := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  // Do not execute the app immediately after installation
  // We will handle execution after the "Finish" button is clicked
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  // Handle the checkbox for "Run after install"
  if CurPageID = wpReady then
  begin
    RunAfterInstall := IsTaskSelected('runafterinstall');
  end;

  // Open the application when the "Finish" button is clicked
  if CurPageID = wpFinished then
  begin
    if RunAfterInstall then
    begin
      // Run the installed application after the user clicks "Finish"
      Exec(ExpandConstant('{app}\GIFjet.exe'), '', '', SW_SHOWNORMAL, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;
