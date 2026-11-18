@echo off
:: ============================================================================
:: Containment Length Calculator - Installer
:: ============================================================================
:: This script installs the pyRevit extension by creating a directory junction
:: in pyRevit's extensions folder. Run as Administrator if the junction fails.
:: ============================================================================

setlocal EnableDelayedExpansion

echo.
echo  ============================================================
echo   Containment Length Calculator - Installer
echo  ============================================================
echo.

:: Store the directory where this script lives
set "PLUGIN_DIR=%~dp0"
set "EXT_SOURCE=%PLUGIN_DIR%ContainmentLength.extension"

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
:: Method 1: Try pyRevit CLI to find extension directories
:: -------------------------------------------------------------------
echo  [1/3] Looking for pyRevit installation...

where pyrevit >nul 2>&1
if %errorlevel% equ 0 (
    echo        Found pyRevit CLI.
    echo.

    :: Try to get extensions directory
    for /f "tokens=*" %%i in ('pyrevit extensions paths 2^>nul') do (
        set "PYREVIT_EXT_DIR=%%i"
    )
)

:: -------------------------------------------------------------------
:: Method 2: Search common pyRevit locations
:: -------------------------------------------------------------------
if not defined PYREVIT_EXT_DIR (
    echo  [INFO] pyRevit CLI not found, searching common locations...
    echo.

    :: Common pyRevit extension directories
    set "LOCATIONS="
    set "LOCATIONS=!LOCATIONS!;%APPDATA%\pyRevit-Master\extensions"
    set "LOCATIONS=!LOCATIONS!;%APPDATA%\pyRevit\extensions"
    set "LOCATIONS=!LOCATIONS!;%PROGRAMDATA%\pyRevit\extensions"
    set "LOCATIONS=!LOCATIONS!;C:\pyRevit-Master\extensions"

    for %%L in (!LOCATIONS!) do (
        if exist "%%~L" (
            set "PYREVIT_EXT_DIR=%%~L"
            echo        Found: %%~L
            goto :found_dir
        )
    )

    :: Search for pyRevit in Program Files
    for /d %%D in ("%PROGRAMFILES%\pyRevit*") do (
        if exist "%%D\extensions" (
            set "PYREVIT_EXT_DIR=%%D\extensions"
            echo        Found: %%D\extensions
            goto :found_dir
        )
    )

    for /d %%D in ("%PROGRAMFILES(x86)%\pyRevit*") do (
        if exist "%%D\extensions" (
            set "PYREVIT_EXT_DIR=%%D\extensions"
            echo        Found: %%D\extensions
            goto :found_dir
        )
    )
)

:found_dir
:: -------------------------------------------------------------------
:: Method 3: Ask user
:: -------------------------------------------------------------------
if not defined PYREVIT_EXT_DIR (
    echo.
    echo  [WARNING] Could not auto-detect pyRevit extensions directory.
    echo.
    echo  Please enter the full path to your pyRevit extensions folder.
    echo  Common locations:
    echo    - %APPDATA%\pyRevit\extensions
    echo    - %APPDATA%\pyRevit-Master\extensions
    echo    - C:\pyRevit-Master\extensions
    echo.
    set /p "PYREVIT_EXT_DIR=  Extensions path: "
)

if not defined PYREVIT_EXT_DIR (
    echo.
    echo  [ERROR] No path provided. Installation cancelled.
    pause
    exit /b 1
)

:: Verify target directory exists
if not exist "%PYREVIT_EXT_DIR%" (
    echo.
    echo  [INFO] Creating extensions directory: %PYREVIT_EXT_DIR%
    mkdir "%PYREVIT_EXT_DIR%" 2>nul
    if errorlevel 1 (
        echo  [ERROR] Cannot create directory. Try running as Administrator.
        pause
        exit /b 1
    )
)

echo.
echo  [2/3] Installing extension...
echo        Source: %EXT_SOURCE%
echo        Target: %PYREVIT_EXT_DIR%\ContainmentLength.extension

:: Remove old installation if exists
if exist "%PYREVIT_EXT_DIR%\ContainmentLength.extension" (
    echo.
    echo  [INFO] Removing previous installation...
    rmdir "%PYREVIT_EXT_DIR%\ContainmentLength.extension" 2>nul
    rd /s /q "%PYREVIT_EXT_DIR%\ContainmentLength.extension" 2>nul
)

:: Create directory junction (doesn't require admin for NTFS junctions)
mklink /J "%PYREVIT_EXT_DIR%\ContainmentLength.extension" "%EXT_SOURCE%"

if %errorlevel% neq 0 (
    echo.
    echo  [WARNING] Junction creation failed. Trying file copy instead...
    xcopy "%EXT_SOURCE%" "%PYREVIT_EXT_DIR%\ContainmentLength.extension\" /E /I /Y /Q
    if errorlevel 1 (
        echo.
        echo  [ERROR] Installation failed. Try running as Administrator.
        pause
        exit /b 1
    )
)

echo.
echo  [3/3] Installation complete!
echo.
echo  ============================================================
echo   NEXT STEPS:
echo   1. Close and restart Autodesk Revit
echo   2. Look for the "Containment" tab in the ribbon
echo   3. Select conduits/trays and click "Calculate Length"
echo  ============================================================
echo.

pause
exit /b 0
