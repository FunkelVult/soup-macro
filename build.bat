@echo off
echo ============================================
echo  Soup Macro - Build
echo ============================================
echo.

echo [1/5] Installiere Abhaengigkeiten...
pip install pynput pyinstaller pillow pystray
echo.

echo [2/5] Erstelle Icon aus logo.png...
python make_icon.py
echo.

echo [3/5] Erstelle .exe mit PyInstaller (1-2 Minuten)...
pyinstaller --onefile --windowed ^
  --name "SoupMacro" ^
  --icon=logo.ico ^
  --add-data "logo.png;." ^
  --uac-admin ^
  macro_tool.py
echo.

echo [4/5] Erstelle Windows-Installer mit Inno Setup...
set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
  set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
  set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
)

if defined ISCC (
  %ISCC% setup.iss
  echo.
  echo ============================================
  echo  BUILD ERFOLGREICH!
  echo ============================================
  echo  Installer: Output\SoupMacro_Setup.exe    ^<-- fuer GitHub Release
  echo  Raw .exe:  dist\SoupMacro.exe             ^<-- fuer Auto-Updater (optional)
  echo ============================================
) else (
  echo.
  echo ============================================
  echo  WARNUNG: Inno Setup nicht gefunden!
  echo  Installer wurde NICHT erstellt.
  echo.
  echo  Download: https://jrsoftware.org/isdl.php
  echo  Danach nochmal build.bat ausfuehren.
  echo ============================================
  echo.
  echo  Nur raw .exe verfuegbar: dist\SoupMacro.exe
)
echo.
pause
