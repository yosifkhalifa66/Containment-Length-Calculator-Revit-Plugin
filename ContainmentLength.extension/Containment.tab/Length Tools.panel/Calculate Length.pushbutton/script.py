# -*- coding: utf-8 -*-
"""Calculate total route length of selected conduits, cable trays, and fittings.

Provides horizontal, vertical, and total route lengths for cable
Voltage Drop (VD) and Short Circuit (SC) calculations.

Select conduits, cable trays, and/or their fittings, then run this tool.
Connected fittings between selected elements are auto-detected.
"""

__title__ = "Calculate\nLength"
__author__ = "Containment Length Calculator Plugin"
__doc__ = (
    "Select conduits, cable trays, and/or fittings, "
    "then click to calculate total route length for VD/SC calculations."
)

# =============================================================================
# Imports
# =============================================================================
import clr
import math

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from pyrevit import revit, DB, forms, script

from System.Windows.Forms import (
    Form, Label, Button, GroupBox, TextBox, ScrollBars,
    FormBorderStyle, FormStartPosition, MessageBox,
    MessageBoxButtons, MessageBoxIcon, Clipboard,
    AnchorStyles, FlatStyle, Panel, CheckBox, ComboBox,
    ComboBoxStyle,
)
from System.Drawing import (
    Size, Point, Color, Font, FontStyle, ContentAlignment,
    Icon, SystemIcons,
)

doc = revit.doc
uidoc = revit.uidoc

# =============================================================================
# Constants
# =============================================================================
FEET_TO_METERS = 0.3048
FEET_TO_MM = 304.8

CONDUIT_CAT = int(DB.BuiltInCategory.OST_Conduit)
CONDUIT_FIT_CAT = int(DB.BuiltInCategory.OST_ConduitFitting)
TRAY_CAT = int(DB.BuiltInCategory.OST_CableTray)
TRAY_FIT_CAT = int(DB.BuiltInCategory.OST_CableTrayFitting)

ALL_TARGET_CATS = {CONDUIT_CAT, CONDUIT_FIT_CAT, TRAY_CAT, TRAY_FIT_CAT}
FITTING_CATS = {CONDUIT_FIT_CAT, TRAY_FIT_CAT}
STRAIGHT_CATS = {CONDUIT_CAT, TRAY_CAT}

CAT_NAMES = {
    CONDUIT_CAT: "Conduit",
    CONDUIT_FIT_CAT: "Conduit Fitting",
    TRAY_CAT: "Cable Tray",
    TRAY_FIT_CAT: "Cable Tray Fitting",
}


# =============================================================================
# Helpers
# =============================================================================

def get_id_value(elem_or_id):
    """Safely get integer value of an ElementId across Revit 2020-2023 and 2024+ (Int64)."""
    if elem_or_id is None:
        return None
    eid = getattr(elem_or_id, "Id", elem_or_id)
    if hasattr(eid, "Value"):
        return eid.Value
    if hasattr(eid, "IntegerValue"):
        return eid.IntegerValue
    try:
        return int(eid.ToString())
    except Exception:
        return None


def _cat_id(element):
    """Return integer category id, or None."""
    if element and element.Category:
        return get_id_value(element.Category.Id)
    return None


def is_target(element):
    return _cat_id(element) in ALL_TARGET_CATS


def is_fitting(element):
    return _cat_id(element) in FITTING_CATS


def is_straight(element):
    return _cat_id(element) in STRAIGHT_CATS


def get_category_label(element):
    return CAT_NAMES.get(_cat_id(element), "Unknown")


def get_connectors(element):
    """Retrieve connectors from an element (conduit, tray, or fitting)."""
    try:
        # Conduits & cable trays expose ConnectorManager directly
        cm = getattr(element, "ConnectorManager", None)
        if cm:
            return list(cm.Connectors)
        # Fittings expose it via MEPModel
        mep = getattr(element, "MEPModel", None)
        if mep:
            cm2 = getattr(mep, "ConnectorManager", None)
            if cm2:
                return list(cm2.Connectors)
    except Exception:
        pass
    return []


def _length_from_curve(element):
    """Try to read length + direction from Location.Curve."""
    loc = element.Location
    if loc is None:
        return None
    curve = getattr(loc, "Curve", None)
    if curve is None:
        return None
    total = curve.Length
    p0 = curve.GetEndPoint(0)
    p1 = curve.GetEndPoint(1)
    dx = p1.X - p0.X
    dy = p1.Y - p0.Y
    dz = p1.Z - p0.Z
    horiz = math.sqrt(dx * dx + dy * dy)
    vert = abs(dz)
    return total, horiz, vert


def _length_from_param(element):
    """Try built-in length parameters."""
    for pname in ("Length", "Conduit Length", "Cable Tray Length"):
        p = element.LookupParameter(pname)
        if p and p.HasValue:
            return p.AsDouble()
    return None


def _direction_from_connectors(connectors, known_total=None):
    """Estimate direction components from connector origins."""
    if len(connectors) < 2:
        return None
    points = [c.Origin for c in connectors]
    best_dist = 0.0
    best_pair = None
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = points[i].DistanceTo(points[j])
            if d > best_dist:
                best_dist = d
                best_pair = (points[i], points[j])
    if best_pair is None or best_dist < 1e-9:
        return None
    p0, p1 = best_pair
    dx = p1.X - p0.X
    dy = p1.Y - p0.Y
    dz = p1.Z - p0.Z
    straight = math.sqrt(dx * dx + dy * dy + dz * dz)
    if straight < 1e-9:
        return None
    h_ratio = math.sqrt(dx * dx + dy * dy) / straight
    v_ratio = abs(dz) / straight
    total = known_total if known_total else best_dist
    return total, total * h_ratio, total * v_ratio


def compute_element_length(element):
    """Return (total, horizontal, vertical) in internal feet units."""
    # 1. Curve-based (most accurate for conduits/trays)
    result = _length_from_curve(element)
    if result:
        return result

    # 2. Parameter-based total + connector direction
    param_len = _length_from_param(element)
    conns = get_connectors(element)
    if param_len and param_len > 0:
        dir_result = _direction_from_connectors(conns, param_len)
        if dir_result:
            return dir_result
        # Assume horizontal if direction unknown
        return param_len, param_len, 0.0

    # 3. Pure connector-based (fittings)
    if conns:
        dir_result = _direction_from_connectors(conns)
        if dir_result:
            return dir_result

    return 0.0, 0.0, 0.0


def find_connected_fittings(elements, doc):
    """Walk the connector graph to discover fittings bridging selected runs."""
    known_ids = set(get_id_value(e) for e in elements)
    found = []  # fittings not originally in selection
    queue = list(elements)
    visited = set()

    while queue:
        elem = queue.pop(0)
        eid = get_id_value(elem)
        if eid in visited:
            continue
        visited.add(eid)

        for conn in get_connectors(elem):
            if not conn.IsConnected:
                continue
            try:
                refs = conn.AllRefs
            except Exception:
                continue
            for ref_conn in refs:
                owner = ref_conn.Owner
                oid = get_id_value(owner)
                if oid in known_ids or oid in visited:
                    continue
                if is_fitting(owner):
                    known_ids.add(oid)
                    found.append(owner)
                    queue.append(owner)

    return found


# =============================================================================
# Unit Formatting
# =============================================================================

def fmt(feet, unit="m"):
    if unit == "m":
        return "{:.3f} m".format(feet * FEET_TO_METERS)
    if unit == "mm":
        return "{:.0f} mm".format(feet * FEET_TO_MM)
    if unit == "ft":
        return "{:.4f} ft".format(feet)
    return "{:.3f}".format(feet)


# =============================================================================
# Results Window (WinForms)
# =============================================================================

class ResultsForm(Form):
    """Modal dialog showing the computed lengths."""

    BLUE = Color.FromArgb(31, 55, 110)
    GREEN = Color.FromArgb(0, 120, 60)
    LIGHT_BG = Color.FromArgb(248, 249, 250)

    def __init__(self, results):
        self.res = results
        self.unit = "m"
        self._build()

    # ---- layout --------------------------------------------------------
    def _build(self):
        self.Text = "Containment Length Calculator"
        self.Size = Size(720, 680)
        self.MinimumSize = Size(640, 580)
        self.StartPosition = FormStartPosition.CenterScreen
        self.FormBorderStyle = FormBorderStyle.Sizable
        self.BackColor = Color.White
        try:
            self.Icon = SystemIcons.Application
        except Exception:
            pass

        y = 12

        # -- Title -------------------------------------------------------
        y = self._label(
            "CONTAINMENT LENGTH CALCULATOR", y,
            font=Font("Segoe UI", 14, FontStyle.Bold),
            fg=self.BLUE,
        )
        y = self._label(
            "Route lengths for cable Voltage Drop (VD) & Short Circuit (SC) calculations",
            y - 4,
            font=Font("Segoe UI", 9, FontStyle.Italic),
            fg=Color.Gray,
        )
        y += 6

        # -- Unit selector -----------------------------------------------
        unit_lbl = Label()
        unit_lbl.Text = "Display unit:"
        unit_lbl.Font = Font("Segoe UI", 9)
        unit_lbl.Location = Point(22, y + 3)
        unit_lbl.Size = Size(85, 20)
        self.Controls.Add(unit_lbl)

        self.unit_combo = ComboBox()
        self.unit_combo.DropDownStyle = ComboBoxStyle.DropDownList
        self.unit_combo.Items.AddRange(["Meters (m)", "Millimeters (mm)", "Feet (ft)"])
        self.unit_combo.SelectedIndex = 0
        self.unit_combo.Location = Point(108, y)
        self.unit_combo.Size = Size(150, 24)
        self.unit_combo.Font = Font("Segoe UI", 9)
        self.unit_combo.SelectedIndexChanged += self._on_unit_change
        self.Controls.Add(self.unit_combo)
        y += 34

        # -- Summary group -----------------------------------------------
        self.summary_group = GroupBox()
        self.summary_group.Text = "  Summary  "
        self.summary_group.Font = Font("Segoe UI", 10, FontStyle.Bold)
        self.summary_group.ForeColor = self.BLUE
        self.summary_group.Location = Point(18, y)
        self.summary_group.Size = Size(666, 200)
        self.summary_group.Anchor = (
            AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right
        )
        self.Controls.Add(self.summary_group)
        y += 210

        # -- Breakdown group ---------------------------------------------
        self.breakdown_group = GroupBox()
        self.breakdown_group.Text = "  Breakdown by Type  "
        self.breakdown_group.Font = Font("Segoe UI", 10, FontStyle.Bold)
        self.breakdown_group.ForeColor = self.BLUE
        self.breakdown_group.Location = Point(18, y)
        self.breakdown_group.Size = Size(666, 200)
        self.breakdown_group.Anchor = (
            AnchorStyles.Top | AnchorStyles.Left
            | AnchorStyles.Right | AnchorStyles.Bottom
        )
        self.Controls.Add(self.breakdown_group)

        self.breakdown_box = TextBox()
        self.breakdown_box.Multiline = True
        self.breakdown_box.ReadOnly = True
        self.breakdown_box.ScrollBars = ScrollBars.Both
        self.breakdown_box.WordWrap = False
        self.breakdown_box.Font = Font("Consolas", 9)
        self.breakdown_box.BackColor = self.LIGHT_BG
        self.breakdown_box.ForeColor = Color.Black
        self.breakdown_box.Location = Point(10, 24)
        self.breakdown_box.Size = Size(644, 166)
        self.breakdown_box.Anchor = (
            AnchorStyles.Top | AnchorStyles.Left
            | AnchorStyles.Right | AnchorStyles.Bottom
        )
        self.breakdown_group.Controls.Add(self.breakdown_box)
        y += 210

        # -- Buttons -----------------------------------------------------
        btn_copy = Button()
        btn_copy.Text = "📋  Copy to Clipboard"
        btn_copy.Font = Font("Segoe UI", 9, FontStyle.Bold)
        btn_copy.Size = Size(175, 38)
        btn_copy.Location = Point(18, y)
        btn_copy.BackColor = self.BLUE
        btn_copy.ForeColor = Color.White
        btn_copy.FlatStyle = FlatStyle.Flat
        btn_copy.FlatAppearance.BorderSize = 0
        btn_copy.Anchor = AnchorStyles.Bottom | AnchorStyles.Left
        btn_copy.Click += self._on_copy
        self.Controls.Add(btn_copy)

        btn_close = Button()
        btn_close.Text = "Close"
        btn_close.Font = Font("Segoe UI", 9)
        btn_close.Size = Size(100, 38)
        btn_close.Location = Point(584, y)
        btn_close.Anchor = AnchorStyles.Bottom | AnchorStyles.Right
        btn_close.Click += lambda s, e: self.Close()
        self.Controls.Add(btn_close)

        # Populate data
        self._refresh()

    # ---- tiny layout helper -------------------------------------------
    def _label(self, text, y, font=None, fg=None):
        lbl = Label()
        lbl.Text = text
        lbl.Font = font or Font("Segoe UI", 9)
        lbl.ForeColor = fg or Color.Black
        lbl.Location = Point(22, y)
        lbl.AutoSize = True
        lbl.MaximumSize = Size(680, 0)
        self.Controls.Add(lbl)
        return y + lbl.PreferredHeight + 4

    # ---- data rendering -----------------------------------------------
    def _refresh(self):
        u = self.unit
        r = self.res

        # Rebuild summary labels inside the group
        self.summary_group.Controls.Clear()

        rows = [
            ("Elements processed:", str(r["total_count"]), False),
            ("    Conduits:", str(r["conduit_count"]), False),
            ("    Cable Trays:", str(r["tray_count"]), False),
            ("    Fittings (auto-included):", str(r["fitting_count"]), False),
            (None, None, False),  # spacer
            ("Total Route Length:", fmt(r["total_length"], u), True),
            ("    Horizontal component:", fmt(r["total_horiz"], u), False),
            ("    Vertical component:", fmt(r["total_vert"], u), False),
        ]

        sy = 28
        for lbl_text, val_text, bold in rows:
            if lbl_text is None:
                sy += 8
                continue
            lbl = Label()
            lbl.Text = lbl_text
            lbl.Font = Font(
                "Segoe UI", 10 if bold else 9,
                FontStyle.Bold if bold else FontStyle.Regular,
            )
            lbl.ForeColor = Color.Black
            lbl.Location = Point(16, sy)
            lbl.Size = Size(310, 22)
            self.summary_group.Controls.Add(lbl)

            val = Label()
            val.Text = val_text
            val.Font = Font(
                "Segoe UI", 10 if bold else 9,
                FontStyle.Bold if bold else FontStyle.Regular,
            )
            val.ForeColor = self.GREEN if bold else Color.Black
            val.Location = Point(330, sy)
            val.Size = Size(320, 22)
            self.summary_group.Controls.Add(val)
            sy += 22

        # Breakdown table
        hdr = "{:<24s} {:>6s} {:>14s} {:>14s} {:>14s}".format(
            "Type", "Count", "Horizontal", "Vertical", "Total"
        )
        sep = "-" * 76
        lines = [hdr, sep]

        for name in sorted(r["by_type"]):
            d = r["by_type"][name]
            lines.append(
                "{:<24s} {:>6d} {:>14s} {:>14s} {:>14s}".format(
                    name, d["count"],
                    fmt(d["horiz"], u), fmt(d["vert"], u), fmt(d["total"], u),
                )
            )

        lines.append(sep)
        lines.append(
            "{:<24s} {:>6d} {:>14s} {:>14s} {:>14s}".format(
                "GRAND TOTAL", r["total_count"],
                fmt(r["total_horiz"], u), fmt(r["total_vert"], u),
                fmt(r["total_length"], u),
            )
        )
        self.breakdown_box.Text = "\r\n".join(lines)

    # ---- events -------------------------------------------------------
    def _on_unit_change(self, sender, args):
        idx = self.unit_combo.SelectedIndex
        self.unit = ["m", "mm", "ft"][idx]
        self._refresh()

    def _on_copy(self, sender, args):
        u = self.unit
        r = self.res
        lines = [
            "CONTAINMENT LENGTH CALCULATION RESULTS",
            "=" * 50,
            "",
            "Elements processed: {}".format(r["total_count"]),
            "  Conduits: {}".format(r["conduit_count"]),
            "  Cable Trays: {}".format(r["tray_count"]),
            "  Fittings: {}".format(r["fitting_count"]),
            "",
            "TOTAL ROUTE LENGTH:  {}".format(fmt(r["total_length"], u)),
            "  Horizontal:        {}".format(fmt(r["total_horiz"], u)),
            "  Vertical:          {}".format(fmt(r["total_vert"], u)),
            "",
            "BREAKDOWN BY TYPE",
            "-" * 50,
        ]
        for name in sorted(r["by_type"]):
            d = r["by_type"][name]
            lines.append(
                "  {}: {} pcs | H={} | V={} | Total={}".format(
                    name, d["count"],
                    fmt(d["horiz"], u), fmt(d["vert"], u), fmt(d["total"], u),
                )
            )
        try:
            Clipboard.SetText("\r\n".join(lines))
            MessageBox.Show(
                "Results copied to clipboard!",
                "Copied",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information,
            )
        except Exception as ex:
            MessageBox.Show(
                "Could not copy: {}".format(ex),
                "Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning,
            )


# =============================================================================
# Main
# =============================================================================

def main():
    sel_ids = uidoc.Selection.GetElementIds()

    if not sel_ids or sel_ids.Count == 0:
        forms.alert(
            "No elements selected!\n\n"
            "Please select conduits, cable trays, and/or their fittings "
            "in the model view, then run this tool again.",
            title="Containment Length Calculator",
            warn_icon=True,
        )
        return

    # --- Gather target elements ----------------------------------------
    selected = []
    skipped = 0
    for eid in sel_ids:
        elem = doc.GetElement(eid)
        if elem and is_target(elem):
            selected.append(elem)
        else:
            skipped += 1

    if not selected:
        forms.alert(
            "None of the selected elements are conduits, cable trays, "
            "or their fittings.\n\n"
            "Please select the correct elements and try again.",
            title="Containment Length Calculator",
            warn_icon=True,
        )
        return

    # --- Auto-discover connected fittings ------------------------------
    auto_fittings = find_connected_fittings(selected, doc)

    # Merge & deduplicate
    seen = set()
    unique = []
    for elem in selected + auto_fittings:
        eid = get_id_value(elem)
        if eid not in seen:
            seen.add(eid)
            unique.append(elem)

    # --- Compute -------------------------------------------------------
    results = {
        "total_length": 0.0,
        "total_horiz": 0.0,
        "total_vert": 0.0,
        "total_count": 0,
        "conduit_count": 0,
        "tray_count": 0,
        "fitting_count": 0,
        "by_type": {},
    }

    for elem in unique:
        total, horiz, vert = compute_element_length(elem)
        label = get_category_label(elem)

        results["total_length"] += total
        results["total_horiz"] += horiz
        results["total_vert"] += vert
        results["total_count"] += 1

        cid = _cat_id(elem)
        if cid == CONDUIT_CAT:
            results["conduit_count"] += 1
        elif cid == TRAY_CAT:
            results["tray_count"] += 1
        elif cid in FITTING_CATS:
            results["fitting_count"] += 1

        bucket = results["by_type"].setdefault(
            label, {"count": 0, "total": 0.0, "horiz": 0.0, "vert": 0.0}
        )
        bucket["count"] += 1
        bucket["total"] += total
        bucket["horiz"] += horiz
        bucket["vert"] += vert

    # --- Show results --------------------------------------------------
    dlg = ResultsForm(results)
    dlg.ShowDialog()


# Entry point
if __name__ == "__main__":
    main()
else:
    main()
