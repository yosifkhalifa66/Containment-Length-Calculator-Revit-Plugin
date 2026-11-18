@echo off
:: ============================================================================
:: Containment Length Calculator - Installer
:: ============================================================================

setlocal EnableDelayedExpansion

echo.
echo  ============================================================
echo   Containment Length Calculator - Installer
echo  ============================================================
echo.

set "PLUGIN_DIR=%~dp0"
:: Remove trailing backslash if present
if "%PLUGIN_DIR:~-1%"=="\" set "PLUGIN_DIR=%PLUGIN_DIR:~0,-1%"
set "EXT_SOURCE=%PLUGIN_DIR%\ContainmentLength.extension"

:: Verify source exists
if not exist "%EXT_SOURCE%" (
    echo  [ERROR] Cannot find ContainmentLength.extension folder.
    echo          Expected at: %EXT_SOURCE%
    echo          Make sure this script is in the plugin root directory.
    echo.
    pause
    exit /b 1
)

:: -------------------------------------------------------------------
:: Method 1: pyRevit CLI (Official and cleanest method)
:: -------------------------------------------------------------------
echo  [1/2] Checking for pyRevit CLI...

where pyrevit >nul 2>&1
if %errorlevel% equ 0 (
    echo        Found pyRevit CLI. Registering extension path directly...
    pyrevit extensions paths add "%PLUGIN_DIR%" >nul 2>&1
    if !errorlevel! equ 0 (
        echo        Successfully registered extension with pyRevit!
        goto :success
    )
)

:: -------------------------------------------------------------------
:: Method 2: Link or copy into pyRevit extensions folder
:: -------------------------------------------------------------------
echo.
echo  [2/2] Linking extension folder...

set "TARGET_DIR="

:: Check common pyRevit extension directories
if exist "%APPDATA%\pyRevit\Extensions" set "TARGET_DIR=%APPDATA%\pyRevit\Extensions"
if not defined TARGET_DIR (
    if exist "%APPDATA%\pyRevit-Master\extensions" set "TARGET_DIR=%APPDATA%\pyRevit-Master\extensions"
)
if not defined TARGET_DIR (
    if exist "%PROGRAMDATA%\pyRevit\Extensions" set "TARGET_DIR=%PROGRAMDATA%\pyRevit\Extensions"
)

:: If none exist, create the standard user AppData extensions folder
if not defined TARGET_DIR (
    set "TARGET_DIR=%APPDATA%\pyRevit\Extensions"
    if not exist "!TARGET_DIR!" (
        mkdir "!TARGET_DIR!" 2>nul
    )
)

if not exist "!TARGET_DIR!" (
    echo.
    echo  [ERROR] Could not locate or create pyRevit extensions folder:
    echo          !TARGET_DIR!
    echo.
    echo  Please ensure pyRevit is installed on this machine.
    pause
    exit /b 1
)

echo        Target folder: !TARGET_DIR!\ContainmentLength.extension

:: Remove existing link or directory if present
if exist "!TARGET_DIR!\ContainmentLength.extension" (
    rmdir "!TARGET_DIR!\ContainmentLength.extension" 2>nul
    if exist "!TARGET_DIR!\ContainmentLength.extension" (
        rd /s /q "!TARGET_DIR!\ContainmentLength.extension" 2>nul
    )
)

:: Try directory junction first (instant, keeps files in sync)
mklink /J "!TARGET_DIR!\ContainmentLength.extension" "%EXT_SOURCE%" >nul 2>&1
if %errorlevel% neq 0 (
    echo        Junction not supported, copying files instead...
    xcopy "%EXT_SOURCE%" "!TARGET_DIR!\ContainmentLength.extension\" /E /I /Y /Q >nul 2>&1
    if !errorlevel! neq 0 (
        echo  [ERROR] Failed to copy files. Please run as Administrator.
        pause
        exit /b 1
    )
)

:success
echo.
echo  ============================================================
echo   [SUCCESS] Installation complete!
echo.
echo   NEXT STEPS:
echo   1. Close and restart Autodesk Revit
echo   2. Look for the "Containment" tab in the Revit ribbon
echo   3. Select conduits/trays and click "Calculate Length"
echo  ============================================================
echo.

pause
exit /b 0
