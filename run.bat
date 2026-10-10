@echo off
setlocal
cd /d "%~dp0"
title Grid Artefact Removal demo

rem The environment lives in a SHORT path: Windows limits paths to 260 characters and PyTorch has very long file names.
set "VENV=%USERPROFILE%\GridAppEnv"
set "P=%PORT%"
if "%P%"=="" set "P=5000"

rem ---- find Python 3.9 or newer ----
set "PY="
py -3 -c "import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)" >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if defined PY goto havepy
python -c "import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)" >nul 2>nul
if not errorlevel 1 set "PY=python"
if defined PY goto havepy
echo.
echo Python 3.9 or newer was not found.
echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH", then run this file again.
echo.
pause
exit /b 1

:havepy
if exist "%VENV%\Scripts\python.exe" goto haveenv
echo Creating the environment in %VENV% - first run only...
%PY% -m venv "%VENV%"
if errorlevel 1 goto envfail

:haveenv
rem ---- install packages unless they already import correctly ----
"%VENV%\Scripts\python.exe" -c "import flask, torch, segmentation_models_pytorch" >nul 2>nul
if not errorlevel 1 goto launch
echo Installing packages - first run only, needs internet, takes a few minutes...
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip
"%VENV%\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto installfail

:launch
echo.
echo Starting the app. Your browser will open at http://127.0.0.1:%P%
echo Close this window or press Ctrl+C to stop the app.
echo.
if defined NO_BROWSER goto run
start "" /min cmd /c "timeout /t 6 /nobreak >nul & start http://127.0.0.1:%P%"
:run
set "PORT=%P%"
"%VENV%\Scripts\python.exe" app.py
echo.
echo The app has stopped. If this was unexpected, see README.md - Troubleshooting.
pause
exit /b 0

:envfail
echo.
echo Could not create the environment. See README.md - Troubleshooting.
pause
exit /b 1

:installfail
echo.
echo Package installation failed. See README.md - Troubleshooting.
pause
exit /b 1
