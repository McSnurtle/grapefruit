@echo OFF

echo "Running installation for https://github.com/McSnurtle/gbro.git"

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%\.."

:: python installations
@for /f "tokens=*" %%i in ('python3 --version 2^>^&1') do @echo Using %%i
python3 -m venv venv
call .\venv\Scripts\activate
echo "Upgrading dependencies..."
pip install --upgrade --verbose -r requirements.txt
deactivate

pause

