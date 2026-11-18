# Containment Length Calculator Plugin

A **pyRevit** extension for Autodesk Revit that calculates the total route length of selected **conduits** and **cable trays** — including their fittings — for use in cable **Voltage Drop (VD)** and **Short Circuit (SC)** calculations.

![Revit Add-In](https://img.shields.io/badge/Revit-Add--In-blue)
![pyRevit](https://img.shields.io/badge/pyRevit-Extension-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

- **Total route length** of selected conduits, cable trays, and fittings
- **Horizontal & vertical breakdown** — essential for accurate VD/SC calculations
- **Auto-detects connected fittings** between selected elements
- **Unit switching** — toggle between Meters, Millimeters, and Feet
- **Copy to clipboard** — paste results directly into your calculation sheets
- **Works with mixed selections** — conduits, trays, and fittings all at once
- **Dark theme icon** included for Revit dark UI

## How It Works

1. **Select** conduits, cable trays, and/or fittings in your Revit model
2. **Click** the "Calculate Length" button in the **Containment** ribbon tab
3. The plugin automatically finds connected fittings you may have missed
4. **View** the results window with:
   - Total route length
   - Horizontal component
   - Vertical component
   - Breakdown by element type (conduit, tray, conduit fitting, tray fitting)

## Installation

### Quick Install (Recommended)

1. **Download or clone** this repository
2. **Run `install.bat`** (double-click it)
3. The installer will:
   - Find your pyRevit extensions directory automatically
   - Create a link to the extension
4. **Restart Revit** — the "Containment" tab will appear in the ribbon

### Manual Install

If the installer can't find pyRevit automatically:

1. Open **pyRevit Settings** in Revit → Custom Extension Directories
2. Add the path to this plugin's root folder (the folder containing `ContainmentLength.extension`)
3. **Reload pyRevit** or restart Revit

### Uninstall

Run `uninstall.bat` or manually delete `ContainmentLength.extension` from your pyRevit extensions directory.

## Requirements

- **Autodesk Revit** 2020 or later
- **pyRevit** 4.x or later (must be installed and working)

## Project Structure

```
Containment Length Calculator Plugin/
├── install.bat                        # One-click installer
├── uninstall.bat                      # Uninstaller
├── README.md                          # This file
├── create_icon.py                     # Icon generator script
└── ContainmentLength.extension/       # pyRevit extension
    ├── extension.json                 # Extension metadata
    └── Containment.tab/              # Ribbon tab
        └── Length Tools.panel/       # Ribbon panel
            └── Calculate Length.pushbutton/
                ├── bundle.yaml       # Button configuration
                ├── script.py         # Main plugin logic
                ├── icon.png          # Light theme icon
                └── icon_dark.png     # Dark theme icon
```

## Technical Details

### Length Calculation Method

The plugin uses three methods to determine element lengths, in order of priority:

1. **Location Curve** — For straight conduits/trays, reads the geometric curve directly
2. **Length Parameter** — Falls back to Revit's built-in `Length` parameter
3. **Connector Distance** — For fittings, calculates distance between connector origins

### Horizontal vs Vertical

- Direction is determined from the element's start and end points
- **Horizontal** = the component in the XY plane (√(dx² + dy²))
- **Vertical** = the component along the Z axis (|dz|)
- For fittings without clear geometry, the direction is estimated from connector positions

### Auto-Detection of Fittings

When you select conduits or trays, the plugin walks the **connector graph** to find fittings that bridge selected elements. This ensures you get the complete route length without manually selecting every fitting.

## License

MIT License — see [LICENSE](LICENSE) for details.
