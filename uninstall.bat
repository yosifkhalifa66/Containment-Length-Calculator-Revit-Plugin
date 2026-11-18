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

:: Search for the extension in common locations
set "REMOVED=0"

set "LOCATIONS="
set "LOCATIONS=!LOCATIONS!;%APPDATA%\pyRevit-Master\extensions"
set "LOCATIONS=!LOCATIONS!;%APPDATA%\pyRevit\extensions"
set "LOCATIONS=!LOCATIONS!;%PROGRAMDATA%\pyRevit\extensions"
set "LOCATIONS=!LOCATIONS!;C:\pyRevit-Master\extensions"

for %%L in (!LOCATIONS!) do (
    if exist "%%~L\ContainmentLength.extension" (
        echo  Found installation at: %%~L\ContainmentLength.extension
        echo  Removing...
        rmdir "%%~L\ContainmentLength.extension" 2>nul
        if exist "%%~L\ContainmentLength.extension" (
            rd /s /q "%%~L\ContainmentLength.extension" 2>nul
        )
        set "REMOVED=1"
        echo  Removed.
    )
)

if "!REMOVED!"=="0" (
    echo  [INFO] No installation found in common locations.
    echo.
    echo  If you installed to a custom location, manually delete
    echo  the "ContainmentLength.extension" folder from your
    echo  pyRevit extensions directory.
) else (
    echo.
    echo  Uninstallation complete.
    echo  Restart Revit for changes to take effect.
)

echo.
pause
exit /b 0
