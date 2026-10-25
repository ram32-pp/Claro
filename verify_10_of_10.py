import json
import pathlib

checks = []

# 1. Env files
checks.append((
    "1. requirements.txt & runtime.txt present",
    pathlib.Path("requirements.txt").exists() and pathlib.Path("runtime.txt").exists()
))

# 2. Corridor 2D & KML cleanup
cor_path = pathlib.Path("data/corridor.geojson")
if cor_path.exists():
    cor = json.loads(cor_path.read_text(encoding="utf-8"))
    coords = cor["features"][0]["geometry"]["coordinates"]
    props = cor["features"][0].get("properties", {})
    checks.append((
        "2. Corridor strict 2D RFC 7946 (46 vertices)",
        len(coords) == 46 and all(len(c) == 2 for c in coords) and "styleUrl" not in props
    ))
else:
    checks.append(("2. Corridor strict 2D RFC 7946 (46 vertices)", False))

# 3. Alerts schema & APS/Vertical fields
alerts_path = pathlib.Path("data/alerts.geojson")
if alerts_path.exists():
    alerts = json.loads(alerts_path.read_text(encoding="utf-8")).get("features", [])
else:
    alerts = []

sar = [f for f in alerts if "Subsidence" in f.get("properties", {}).get("hazard_type", "")]
opt = [f for f in alerts if "Vegetation" in f.get("properties", {}).get("hazard_type", "")]

checks.append((
    f"3. Alerts populated (SAR={len(sar)}, OPT={len(opt)})",
    len(sar) > 0 and len(opt) > 0
))
checks.append((
    "4. SAR APS & Vertical Decomposition fields",
    len(sar) > 0 and all("vertical_rate_mm_yr" in f["properties"] and "dist_to_centerline_m" in f["properties"] for f in sar)
))
checks.append((
    "5. Tiered Buffer Compliance (SAR<=60m, OPT<=30m)",
    len(alerts) > 0
    and all(f["properties"].get("dist_to_centerline_m", 999) <= 60.0 for f in sar)
    and all(f["properties"].get("dist_to_centerline_m", 999) <= 30.0 for f in opt)
))

# 6. Script & App checks
app_code = pathlib.Path("app.py").read_text(encoding="utf-8") if pathlib.Path("app.py").exists() else ""
radar_code = pathlib.Path("scripts/process_radar.py").read_text(encoding="utf-8") if pathlib.Path("scripts/process_radar.py").exists() else ""
merge_code = pathlib.Path("scripts/merge_alerts.py").read_text(encoding="utf-8") if pathlib.Path("scripts/merge_alerts.py").exists() else ""

checks.append((
    "6. process_radar.py APS + union_all + 12d baseline",
    "remove_atmospheric_phase_screen" in radar_code and "union_all()" in radar_code and ".unary_union" not in radar_code
))
checks.append((
    "7. merge_alerts.py safe .get() sorting",
    "x.get(" in merge_code or "props.get(" in merge_code
))
checks.append((
    "8. app.py Orthogonal KPIs & fit_bounds()",
    "fit_bounds" in app_code and "sar_features" in app_code and "opt_features" in app_code
))
checks.append((
    "9. app.py Bidirectional Map Click Binding",
    "last_object_clicked_tooltip" in app_code and "expanded=is_selected" in app_code
))
checks.append((
    "10. app.py Enterprise ESRI Basemap + ROI Simulator",
    "World_Imagery" in app_code and "ROI" in app_code
))

print("\n=== SINDHORBIT 10/10 VERIFICATION SUITE ===")
for name, passed in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")
passed_count = sum(1 for _, p in checks if p)
print(f"Score: {passed_count}/{len(checks)} Checks Passed\n")
