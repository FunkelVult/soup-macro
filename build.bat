@echo off
echo ============================================
echo  Macro Tool - Build
echo ============================================
echo.

echo [1/4] Installiere Abhaengigkeiten...
pip install pynput pyinstaller pillow pystray
echo.

echo [2/4] Erstelle Icon aus logo.png...
python make_icon.py
echo.

echo [3/4] Erstelle .exe (1-2 Minuten)...
pyinstaller --onefile --windowed ^
  --name "SoupMacro" ^
  --icon=logo.ico ^
  --add-data "logo.png;." ^
  --uac-admin ^
  macro_tool.py
echo.

echo [4/4] Fertig!
echo Die .exe liegt in:  dist\SoupMacro.exe
echo.
pause
