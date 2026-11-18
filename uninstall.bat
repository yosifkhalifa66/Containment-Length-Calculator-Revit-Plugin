@echo off
:: ============================================================================
:: Containment Length Calculator - Uninstaller
:: ============================================================================

setlocal EnableDelayedExpansion

echo.
echo  ============================================================
echo   Containment Length Calculator - Uninstaller
echo  ============================================================
echo.

set "PLUGIN_DIR=%~dp0"
if "%PLUGIN_DIR:~-1%"=="\" set "PLUGIN_DIR=%PLUGIN_DIR:~0,-1%"

:: Check if pyRevit CLI is available to remove the registered search path
where pyrevit >nul 2>&1
if %errorlevel% equ 0 (
    echo  Unregistering extension path from pyRevit...
    pyrevit extensions paths forget "%PLUGIN_DIR%" >nul 2>&1
)

:: Also clean up any linked or copied directories in common locations
set "LOCATIONS="
set "LOCATIONS=!LOCATIONS!;%APPDATA%\pyRevit\Extensions"
set "LOCATIONS=!LOCATIONS!;%APPDATA%\pyRevit-Master\extensions"
set "LOCATIONS=!LOCATIONS!;%PROGRAMDATA%\pyRevit\Extensions"

for %%L in (!LOCATIONS!) do (
    if exist "%%~L\ContainmentLength.extension" (
        echo  Removing from: %%~L\ContainmentLength.extension
        rmdir "%%~L\ContainmentLength.extension" 2>nul
        if exist "%%~L\ContainmentLength.extension" (
            rd /s /q "%%~L\ContainmentLength.extension" 2>nul
        )
    )
)

echo.
echo  ============================================================
echo   [SUCCESS] Uninstallation complete!
echo   Restart Revit for changes to take effect.
echo  ============================================================
echo.

pause
exit /b 0
