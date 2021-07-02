!include MUI2.nsh
!include FileFunc.nsh
!include LogicLib.nsh

;--------------------------------
;Perform Machine-level install, if possible

!define MULTIUSER_EXECUTIONLEVEL Highest
;Add support for command-line args that let uninstaller know whether to
;uninstall machine- or user installation:
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!include MultiUser.nsh
!include LogicLib.nsh

Function finishpageaction
CreateShortcut "$desktop\MJOLNIRGui.lnk" "$instdir\MJOLNIRGui.exe"
FunctionEnd


!macro UninstallExisting exitcode uninstcommand
Push `${uninstcommand}`
Call UninstallExisting
Pop ${exitcode}
!macroend
Function UninstallExisting
Exch $1 ; uninstcommand
Push $2 ; Uninstaller
Push $3 ; Len
StrCpy $3 ""
StrCpy $2 $1 1
StrCmp $2 '"' qloop sloop
sloop:
	StrCpy $2 $1 1 $3
	IntOp $3 $3 + 1
	StrCmp $2 "" +2
	StrCmp $2 ' ' 0 sloop
	IntOp $3 $3 - 1
	Goto run
qloop:
	StrCmp $3 "" 0 +2
	StrCpy $1 $1 "" 1 ; Remove initial quote
	IntOp $3 $3 + 1
	StrCpy $2 $1 1 $3
	StrCmp $2 "" +2
	StrCmp $2 '"' 0 qloop
run:
	StrCpy $2 $1 $3 ; Path to uninstaller
	StrCpy $1 161 ; ERROR_BAD_PATHNAME
	GetFullPathName $3 "$2\.." ; $InstDir
	IfFileExists "$2" 0 +4
	ExecWait '"$2" /S _?=$3' $1 ; This assumes the existing uninstaller is a NSIS uninstaller, other uninstallers don't support /S nor _?=
	IntCmp $1 0 "" +2 +2 ; Don't delete the installer if it was aborted
	Delete "$2" ; Delete the uninstaller
	RMDir "$3" ; Try to delete $InstDir
	RMDir "$3\.." ; (Optional) Try to delete the parent of $InstDir
Pop $3
Pop $2
Exch $1 ; exitcode
FunctionEnd


Function .onInit
  !insertmacro MULTIUSER_INIT
  ;Do not use InstallDir at all so we can detect empty $InstDir!
  ReadRegStr $0 HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\MJOLNIRGui" "UninstallString"
  ${If} $0 != ""
  ${AndIf} ${Cmd} `MessageBox MB_YESNO|MB_ICONQUESTION "Previous version of MJOLNIRGui was detected. Do you want to uninstall this version?" /SD IDYES IDYES`
    ExecWait "$0" $1
    ${If} $1 <> 0
      MessageBox MB_YESNO|MB_ICONSTOP "Failed to uninstall, continue anyway?" /SD IDYES IDYES +2
        Abort
    ${EndIf}
  ${EndIf}
  ${If} $InstDir == "" ; /D not used
      ${If} $MultiUser.InstallMode == "AllUsers"
          StrCpy $InstDir "$PROGRAMFILES\MJOLNIRGui"
      ${Else}
          StrCpy $InstDir "$LOCALAPPDATA\MJOLNIRGui"
      ${EndIf}
  ${EndIf}
FunctionEnd

Function un.onInit
  !insertmacro MULTIUSER_UNINIT
FunctionEnd

;--------------------------------
;General

  Name "MJOLNIRGui"
  OutFile "..\MJOLNIRGuiSetup.exe"

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !define MUI_WELCOMEPAGE_TEXT "Welcome to the installation process for MJOLNIRGui.$\r$\nWe hope that you will enjoy this graphical user interface to MJOLNIR.$\r$\n$\r$\nClick Next to continue."
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
    !define MUI_FINISHPAGE_NOAUTOCLOSE
    !define MUI_FINISHPAGE_RUN
    !define MUI_FINISHPAGE_RUN_CHECKED
    !define MUI_FINISHPAGE_SHOWREADME ""
    !define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
    !define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Desktop Shortcut"
    !define MUI_FINISHPAGE_SHOWREADME_FUNCTION finishpageaction
    !define MUI_FINISHPAGE_TEXT 'Thank you for installing MJOLNIRGui. $\r$\nPlease cite the MJOLNIR software using the DOI https://doi.org/10.1016/j.softx.2020.100600 or through $\r$\nhttps://www.psi.ch/en/sinq/camea/data-treatment'
    !define MUI_FINISHPAGE_RUN_TEXT "Run MJOLNIRGui"
    !define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"
       
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

!define UNINST_KEY \
  "Software\Microsoft\Windows\CurrentVersion\Uninstall\MJOLNIRGui"
Section
  SetOutPath "$InstDir"
  File /r "..\MJOLNIRGui\*"
  WriteRegStr SHCTX "Software\MJOLNIRGui" "" $InstDir
  WriteUninstaller "$InstDir\uninstall.exe"
  CreateShortCut "$SMPROGRAMS\MJOLNIRGui.lnk" "$InstDir\MJOLNIRGui.exe"
  WriteRegStr SHCTX "${UNINST_KEY}" "DisplayName" "MJOLNIRGui"
  WriteRegStr SHCTX "${UNINST_KEY}" "UninstallString" \
    "$\"$InstDir\uninstall.exe$\" /$MultiUser.InstallMode"
  WriteRegStr SHCTX "${UNINST_KEY}" "QuietUninstallString" \
    "$\"$InstDir\uninstall.exe$\" /$MultiUser.InstallMode /S"
  WriteRegStr SHCTX "${UNINST_KEY}" "Publisher" "MJOLNIRPackage"
  ${GetSize} "$InstDir" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD SHCTX "${UNINST_KEY}" "EstimatedSize" "$0"

SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  RMDir /r "$InstDir"
  Delete "$SMPROGRAMS\MJOLNIRGui.lnk"
  DeleteRegKey /ifempty SHCTX "Software\MJOLNIRGui"
  DeleteRegKey SHCTX "${UNINST_KEY}"

SectionEnd

Function LaunchLink
  !addplugindir "."
  ShellExecAsUser::ShellExecAsUser "open" "$SMPROGRAMS\MJOLNIRGui.lnk"
FunctionEnd
