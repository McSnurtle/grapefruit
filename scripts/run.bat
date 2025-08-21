@echo OFF

echo "Running grapefruit"

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%\.."

:: python venv
call .\venv\Scripts\activate
python3 src/ui.py
deactivate

pause
