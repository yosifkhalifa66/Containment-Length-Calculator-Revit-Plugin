# 🚀 Containment Length Calculator v1.0.0

**First stable release** — A pyRevit extension for Autodesk Revit that calculates the total route length of conduits and cable trays (including fittings) for cable **Voltage Drop (VD)** and **Short Circuit (SC)** calculations.

---

## ✨ Features

- **Total route length** of selected conduits, cable trays, and their fittings
- **Horizontal & vertical breakdown** — essential for accurate VD/SC cable calculations
- **Auto-detects connected fittings** — walks the Revit connector graph so you don't have to manually select every elbow and tee
- **Unit switching** — toggle live between Meters (m), Millimeters (mm), and Feet (ft)
- **Copy to clipboard** — formatted text ready for pasting into calculation sheets
- **Mixed selection support** — conduits, cable trays, and all fitting types in one go
- **Dark theme icon** included for Revit dark UI

## 📋 Requirements

- **Autodesk Revit** 2020 or later
- **pyRevit** 4.x or later (must be installed and working)

## 📥 Installation

1. Download and extract this release
2. **Double-click `install.bat`** — it auto-detects your pyRevit extensions directory
3. **Restart Revit** — a **"Containment"** tab appears in the ribbon
4. Select conduits/trays → click **"Calculate Length"**

### Manual Installation (Alternative)
- Open **pyRevit Settings** → Custom Extension Directories
- Add the path to the extracted folder (the one containing `ContainmentLength.extension`)
- Reload pyRevit or restart Revit

## 🔧 How It Works

| Step | Action |
|---|---|
| 1 | Select conduits, cable trays, and/or fittings in your Revit model |
| 2 | Click **Calculate Length** in the **Containment** ribbon tab |
| 3 | Plugin auto-discovers connected fittings between selected runs |
| 4 | View results: total, horizontal, vertical lengths + per-type breakdown |
| 5 | Switch units or copy results to clipboard |

## 📐 Technical Details

### Length Calculation Methods (priority order)
1. **Location Curve** — reads the geometric curve directly for straight runs
2. **Length Parameter** — falls back to Revit's built-in `Length` parameter
3. **Connector Distance** — calculates distance between connector origins for fittings

### Direction Decomposition
- **Horizontal** = √(dx² + dy²) — component in the XY plane
- **Vertical** = |dz| — component along the Z axis

---

**Full source code and documentation included. MIT Licensed.**
