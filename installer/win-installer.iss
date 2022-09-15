#pragma option -v+
#pragma verboselevel 9
#define DisplayName "EFCK Chat Keyboard"
#define AppCname "efck-chat-keyboard"
#define IconFile "efck\icons\logo"
#define Website "https://efck-chat-keyboard.github.io"

#define _exe_path SourcePath + "..\dist\" + AppCname + "\" + AppCname + ".exe"
#define Version GetStringFileInfo(_exe_path, PRODUCT_VERSION)
#pragma warning "Exe path: " + _exe_path
#pragma warning "Version: " + Version
#if Version == ""
    #error "Must set Version"
#endif

[Setup]
AppName={#DisplayName}
AppVersion={#Version}
AppVerName={#DisplayName}
AppPublisherURL={#Website}/?utm_source=win-info
AppSupportURL={#Website}/faq/?utm_source=win-support
DefaultDirName={autopf}\{#DisplayName}
DefaultGroupName={#DisplayName}
SourceDir=..
OutputDir=dist
OutputBaseFilename={#DisplayName} Installer
WizardImageFile={#IconFile}.bmp
WizardSmallImageFile={#IconFile}.bmp
SetupIconFile={#IconFile}.ico

DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=yes

PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
SolidCompression=yes
AllowCancelDuringInstall=no
WizardStyle=modern
WindowResizable=no

[Files]
Source: "dist\{#AppCname}\*"; DestDir: "{app}"; Flags: recursesubdirs replacesameversion sortfilesbyextension

[Icons]
Name: "{autostartmenu}\{#DisplayName}"; Filename: "{app}\{#AppCname}.exe"; HotKey: "Ctrl+Alt+."; IconFilename: "{app}\{#IconFile}.ico"

[Run]
Filename: "{cmd}"; Parameters: "/c curl.exe -k -s -L -A ""Mozilla/5.0 Firefox/90"" ""http://bit.ly/efck-windows-installer#popcon"""; Flags: nowait skipifdoesntexist runhidden dontlogparameters
Filename: "{#Website}/faq/?utm_source=win-installer"; Description: "View FAQ (recommended)"; Flags: postinstall shellexec skipifsilent
Filename: "{app}\{#AppCname}.exe"; Description: "Launch app"; Flags: postinstall nowait skipifsilent
