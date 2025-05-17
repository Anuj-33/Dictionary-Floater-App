@echo off
REM Check if pyinstaller is installed; install it if not
echo Checking pyinstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing pyinstaller...
    pip install pyinstaller
)

echo.
echo Building dictionary_floater.exe...
REM Use --windowed to suppress console for GUI apps
REM Add --add-data to include dictionary.png in the bundle
pyinstaller --windowed --onefile --icon=dictionary.ico --add-data "dictionary.png;." dictionary_floater.py

echo.
echo Adding to Startup...
set "EXE=%~dp0dist\dictionary_floater.exe"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\DictionaryFloater.lnk"

REM Create a shortcut in the Startup folder
powershell -Command "$s = (New-Object -COM WScript.Shell).CreateShortcut('%STARTUP%'); $s.TargetPath = '%EXE%'; $s.IconLocation = '%EXE%'; $s.Save()"

echo.
echo ✅ Done. Floating dictionary will run at every startup.
pause
