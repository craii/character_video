@echo off
setlocal
set SCRIPT_DIR=%~dp0

"%SCRIPT_DIR%\venv_win\Scripts\python.exe %SCRIPT_DIR%\App_Ps6_blocked.py"

endlocal