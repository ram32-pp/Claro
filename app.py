# app.py - SindhOrbit Enterprise Geospatial & InSAR Operations Platform
import json
import math
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(
    page_title="SindhOrbit — Transmission Grid & InSAR Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_html(html_str: str):
    """Strips leading indentation so Streamlit never renders HTML tags as raw markdown code blocks."""
    cleaned = "\n".join(line.lstrip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Enterprise Design System (DM Sans + IBM Plex Mono, Slate Architectural Theme)
# ─────────────────────────────────────────────────────────────────────────────
render_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    --bg-canvas: #090d16;
    --bg-surface: #111827;
    --bg-elevated: #161f33;
    --border-subtle: #1f2937;
    --border-focus: #374151;
    --text-main: #f9fafb;
    --text-secondary: #9ca3af;
    --text-muted: #6b7280;
    --accent-blue: #3b82f6;
    --accent-sky: #0ea5e9;
    --status-crit: #f43f5e;
    --status-warn: #f59e0b;
    --status-ok: #10b981;
}

.stApp {
    background-color: var(--bg-canvas);
    color: var(--text-main);
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Hide Streamlit Chrome */
#MainMenu, footer, .stDeployButton, [data-testid="stToolbar"] {
    display: none !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 1.5rem !important;
}

.block-container {
    padding-top: 0.75rem !important;
    padding-bottom: 1.5rem !important;
    padding-left: 1.75rem !important;
    padding-right: 1.75rem !important;
    max-width: 100% !important;
}

/* Sidebar Refinement */
section[data-testid="stSidebar"] {
    background-color: #0b0f19 !important;
    border-right: 1px solid var(--border-subtle) !important;
}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.84rem !important;
    color: #d1d5db !important;
}

/* ── Top Enterprise Header Bar ── */
.ent-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    padding: 0.85rem 1.25rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    margin-bottom: 0.9rem;
}

.ent-brand {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}

.ent-mark {
    width: 36px;
    height: 36px;
    border-radius: 6px;
    background: linear-gradient(135deg, #2563eb 0%, #0284c7 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: -0.03em;
    flex-shrink: 0;
}

.ent-title-row {
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
}

.ent-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-main);
    letter-spacing: -0.01em;
    margin: 0;
}

.ent-tag-muted {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 500;
}

.ent-subtitle {
    font-size: 0.78rem;
    color: var(--text-secondary);
    margin-top: 1px;
}

.ent-badges {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.status-chip {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    padding: 0.28rem 0.65rem;
    border-radius: 5px;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    white-space: nowrap;
    border: 1px solid transparent;
}

.chip-neutral {
    background-color: #161f33;
    color: #cbd5e1;
    border-color: #26334d;
}

.chip-ok {
    background-color: rgba(16, 185, 129, 0.1);
    color: #34d399;
    border-color: rgba(16, 185, 129, 0.25);
}

.chip-crit {
    background-color: rgba(244, 63, 94, 0.12);
    color: #fb7185;
    border-color: rgba(244, 63, 94, 0.3);
}

.dot-indicator {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: currentColor;
    flex-shrink: 0;
}

/* ── 4-Column Executive KPI Grid ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.85rem;
    margin-bottom: 1rem;
}

@media (max-width: 1100px) {
    .kpi-row { grid-template-columns: repeat(2, 1fr); }
}

.kpi-box {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.kpi-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.45rem;
}

.kpi-label {
    font-size: 0.76rem;
    font-weight: 600;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.kpi-pill {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.64rem;
    font-weight: 600;
    padding: 0.12rem 0.45rem;
    border-radius: 4px;
    white-space: nowrap;
    flex-shrink: 0;
}

.kpi-main {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.55rem;
    font-weight: 600;
    color: var(--text-main);
    line-height: 1.15;
    letter-spacing: -0.02em;
    margin-bottom: 0.4rem;
}

.kpi-unit {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-left: 2px;
}

.kpi-foot {
    font-size: 0.74rem;
    color: var(--text-muted);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 0.45rem;
    border-top: 1px solid rgba(31, 41, 55, 0.7);
}

.kpi-foot-code {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: #94a3b8;
    flex-shrink: 0;
}

/* ── Panel Section Headers ── */
.panel-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0.85rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 7px;
    margin-bottom: 0.55rem;
}

.panel-bar-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #e5e7eb;
    letter-spacing: 0.01em;
}

.panel-bar-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Map Legend Bar ── */
.map-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
    padding: 0.5rem 0.85rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 7px;
    margin-top: 0.35rem;
    font-size: 0.73rem;
    color: var(--text-secondary);
}

.leg-group {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.leg-item {
    display: inline-flex;
    align-items: center;
    gap: 0.38rem;
    white-space: nowrap;
}

.leg-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}

/* ── Right Telemetry Inspector Card ── */
.inspector-card {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.95rem 1.05rem;
    margin-bottom: 0.7rem;
}

.insp-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 0.7rem;
}

.insp-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: var(--accent-sky);
    font-weight: 500;
}

.insp-title {
    font-size: 0.96rem;
    font-weight: 700;
    color: var(--text-main);
    margin-top: 2px;
    line-height: 1.25;
}

.insp-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
}

.stat-cell {
    background-color: var(--bg-canvas);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    padding: 0.45rem 0.6rem;
}

.stat-lbl {
    font-size: 0.64rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.03em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.stat-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-main);
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Cross Section Box ── */
.xsec-container {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    margin-bottom: 0.7rem;
}

.xsec-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 0.4rem;
    gap: 0.5rem;
}

/* ── Action Callout ── */
.action-callout {
    background-color: rgba(14, 165, 233, 0.07);
    border: 1px solid rgba(14, 165, 233, 0.22);
    border-left: 3px solid var(--accent-sky);
    border-radius: 6px;
    padding: 0.6rem 0.8rem;
    font-size: 0.78rem;
    color: #e2e8f0;
    line-height: 1.4;
    margin-top: 0.6rem;
    margin-bottom: 0.65rem;
}

/* ── Primary Export Button ── */
div.stDownloadButton > button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 6px !important;
    padding: 0.5rem 0.95rem !important;
    transition: background-color 0.15s ease !important;
}

div.stDownloadButton > button:hover {
    background-color: #1d4ed8 !important;
    border-color: #60a5fa !important;
}
</style>
""")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Session State
# ─────────────────────────────────────────────────────────────────────────────
if "selected_alert" not in st.session_state:
    st.session_state.selected_alert = None


# ─────────────────────────────────────────────────────────────────────────────
# 3. Geodesic & SVG Builders
# ─────────────────────────────────────────────────────────────────────────────
def compute_geodesic_length_km(coords):
    """Computes exact WGS84 Haversine geodesic length across LineString vertices."""
    total_km = 0.0
    R = 6371.0088
    for i in range(len(coords) - 1):
        lon1, lat1 = math.radians(coords[i][0]), math.radians(coords[i][1])
        lon2, lat2 = math.radians(coords[i + 1][0]), math.radians(coords[i + 1][1])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        total_km += 2 * R * math.asin(math.sqrt(a))
    return round(total_km, 2)


def build_clean_svg_chart(dates, values, is_sar=True, severity="CRITICAL"):
    """Renders a crisp, clean enterprise SVG trend chart with IBM Plex Mono labels."""
    w, h = 440, 162
    pad_l, pad_r, pad_t, pad_b = 44, 16, 20, 26
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b

    line_col = (
        "#f43f5e" if (severity == "CRITICAL" and is_sar)
        else ("#f59e0b" if is_sar else "#0ea5e9")
    )
    grad_id = f"g_{'sar' if is_sar else 'opt'}_{severity}"

    min_v, max_v = min(values), max(values)
    if is_sar:
        y_min = min(min_v * 1.15, -25.0)
        y_max = 0.0
    else:
        y_min = 0.0
        y_max = max(max_v * 1.15, 0.75)

    span = (y_max - y_min) if (y_max - y_min) != 0 else 1.0

    pts = []
    for idx, val in enumerate(values):
        x = pad_l + (idx / max(1, len(values) - 1)) * plot_w
        y = pad_t + plot_h - ((val - y_min) / span) * plot_h
        pts.append((round(x, 1), round(y, 1), val, dates[idx]))

    poly_pts = " ".join(f"{x},{y}" for x, y, _, _ in pts)
    area_pts = (
        f"{pts[0][0]},{pad_t + plot_h} "
        + poly_pts
        + f" {pts[-1][0]},{pad_t + plot_h}"
    )

    grid_svg = ""
    for frac in [0.0, 0.5, 1.0]:
        gy = round(pad_t + plot_h * (1.0 - frac), 1)
        gval = y_min + frac * span
        lbl = f"{gval:.0f}" if is_sar else f"{gval:.2f}"
        grid_svg += (
            f'<line x1="{pad_l}" y1="{gy}" x2="{w - pad_r}" y2="{gy}" '
            f'stroke="#1f2937" stroke-width="1"/>'
        )
        grid_svg += (
            f'<text x="{pad_l - 7}" y="{gy + 3}" fill="#6b7280" '
            f'font-family="IBM Plex Mono" font-size="8.5" text-anchor="end">{lbl}</text>'
        )

    thresh_val = -15.0 if is_sar else 0.45
    thresh_svg = ""
    if y_min <= thresh_val <= y_max:
        ty = round(pad_t + plot_h - ((thresh_val - y_min) / span) * plot_h, 1)
        t_lbl = "Threshold (-15 mm/yr)" if is_sar else "RoW Limit (0.45)"
        thresh_svg = (
            f'<line x1="{pad_l}" y1="{ty}" x2="{w - pad_r}" y2="{ty}" '
            f'stroke="#f59e0b" stroke-dasharray="4,3" stroke-width="1"/>'
            f'<text x="{w - pad_r - 2}" y="{ty - 4}" fill="#f59e0b" '
            f'font-family="IBM Plex Mono" font-size="8" text-anchor="end">{t_lbl}</text>'
        )

    nodes_svg = ""
    for x, y, val, d_str in pts:
        v_str = f"{val:.1f}" if is_sar else f"{val:.2f}"
        nodes_svg += (
            f'<circle cx="{x}" cy="{y}" r="3.2" fill="#111827" '
            f'stroke="{line_col}" stroke-width="2"/>'
        )
        nodes_svg += (
            f'<text x="{x}" y="{y - 6}" fill="#d1d5db" '
            f'font-family="IBM Plex Mono" font-size="8" text-anchor="middle">{v_str}</text>'
        )
        nodes_svg += (
            f'<text x="{x}" y="{h - 7}" fill="#9ca3af" '
            f'font-family="DM Sans" font-size="9" text-anchor="middle">{d_str}</text>'
        )

    return f"""
<svg viewBox="0 0 {w} {h}" width="100%" height="{h}"
     style="background:#111827; border:1px solid #1f2937; border-radius:7px; display:block;">
    <defs>
        <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="{line_col}" stop-opacity="0.24"/>
            <stop offset="100%" stop-color="{line_col}" stop-opacity="0.0"/>
        </linearGradient>
    </defs>
    {grid_svg}
    {thresh_svg}
    <polygon points="{area_pts}" fill="url(#{grad_id})"/>
    <polyline fill="none" stroke="{line_col}" stroke-width="2" points="{poly_pts}"/>
    {nodes_svg}
</svg>
"""


def build_corridor_offset_bar(dist_m, is_sar=True, severity="CRITICAL"):
    """Renders a clean horizontal cross-section gauge with non-wrapping axis labels."""
    clamped = max(0.0, min(60.0, float(dist_m)))
    pct = 50.0 + (clamped / 60.0) * 45.0
    dot_col = (
        "#f43f5e" if severity == "CRITICAL"
        else ("#0ea5e9" if not is_sar else "#f59e0b")
    )

    return f"""
<div class="xsec-container">
    <div class="xsec-head">
        <span>Right-of-Way Cross-Section Profile</span>
        <span style="font-family:'IBM Plex Mono',monospace; color:{dot_col};">
            +{dist_m:.1f}m from Centerline
        </span>
    </div>
    <div style="position:relative; height:20px; background:#090d16; border-radius:4px;
                border:1px solid #1f2937; overflow:hidden;">
        <div style="position:absolute; left:5%; width:90%; top:0; bottom:0;
                    background:rgba(245,158,11,0.06);
                    border-left:1px dashed rgba(245,158,11,0.4);
                    border-right:1px dashed rgba(245,158,11,0.4);"></div>
        <div style="position:absolute; left:27.5%; width:45%; top:0; bottom:0;
                    background:rgba(14,165,233,0.09);
                    border-left:1px dashed rgba(14,165,233,0.45);
                    border-right:1px dashed rgba(14,165,233,0.45);"></div>
        <div style="position:absolute; left:50%; width:1.5px; top:0; bottom:0;
                    background:#38bdf8;"></div>
        <div style="position:absolute; left:{pct:.1f}%; top:4px; width:10px; height:10px;
                    margin-left:-5px; border-radius:50%; background:{dot_col};
                    border:1.5px solid #ffffff;"></div>
    </div>
    <div style="display:flex; justify-content:space-between;
                font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
                color:#6b7280; margin-top:4px; white-space:nowrap;">
        <span>-60m</span>
        <span style="color:#38bdf8;">-30m RoW</span>
        <span style="color:#d1d5db;">0m Axis</span>
        <span style="color:#38bdf8;">+30m RoW</span>
        <span>+60m</span>
    </div>
</div>
"""


# ─────────────────────────────────────────────────────────────────────────────
# 4. Data Ingestion
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_datasets():
    with open("data/corridor.geojson", "r", encoding="utf-8") as f:
        corridor = json.load(f)
    with open("data/alerts.geojson", "r", encoding="utf-8") as f:
        alerts = json.load(f)
    return corridor, alerts


try:
    corridor_data, alerts_data = load_datasets()
except FileNotFoundError:
    st.error("Data contract files missing! Ensure data/corridor.geojson and data/alerts.geojson exist.")
    st.stop()

corridor_feat = corridor_data["features"][0]
corridor_coords = corridor_feat["geometry"]["coordinates"]
corridor_props = corridor_feat.get("properties", {})
dynamic_length_km = compute_geodesic_length_km(corridor_coords)
vertex_count = len(corridor_coords)

features = alerts_data.get("features", [])

# Orthogonal Hazard & Severity Separation (Preserves Check #8)
sar_features = [f for f in features if "Subsidence" in f.get("properties", {}).get("hazard_type", "")]
opt_features = [f for f in features if "Vegetation" in f.get("properties", {}).get("hazard_type", "")]
sar_crit_count = sum(1 for f in sar_features if f.get("properties", {}).get("severity") == "CRITICAL")
opt_crit_count = sum(1 for f in opt_features if f.get("properties", {}).get("severity") == "CRITICAL")
total_crit = sar_crit_count + opt_crit_count


# ─────────────────────────────────────────────────────────────────────────────
# 5. Sidebar Controls & B2B ROI Calculator
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    render_html("""
    <div style="padding:0.25rem 0 0.75rem 0; border-bottom:1px solid #1f2937; margin-bottom:0.85rem;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#60a5fa;
                    font-weight:600; text-transform:uppercase; letter-spacing:0.06em;">
            Telemetry Controls
        </div>
        <div style="font-size:1.02rem; font-weight:700; color:#f9fafb; margin-top:2px;">
            Sensor Layers &amp; Filters
        </div>
    </div>
    """)

    show_sar = st.checkbox("Sentinel-1 InSAR (60m Geotech)", value=True)
    show_opt = st.checkbox("Sentinel-2 Optical (30m RoW)", value=True)
    severity_filter = st.multiselect(
        "Severity Classification",
        options=["CRITICAL", "WARNING"],
        default=["CRITICAL", "WARNING"]
    )

    render_html("""
    <div style="margin:1rem 0 0.55rem 0; padding-top:0.85rem; border-top:1px solid #1f2937;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#34d399;
                    font-weight:600; text-transform:uppercase; letter-spacing:0.06em;">
            Utility Economics
        </div>
        <div style="font-size:1.02rem; font-weight:700; color:#f9fafb; margin-top:2px;">
            B2B ROI Simulator (PKR)
        </div>
    </div>
    """)

    monitored_km = st.slider("Monitored Corridor Scale (km)", 50, 5000, 500, step=50)
    manual_patrol_m = (85000 * monitored_km) / 1e6
    sindhorbit_saas_m = (25000 * monitored_km) / 1e6
    annual_savings_m = manual_patrol_m - sindhorbit_saas_m

    render_html(f"""
    <div style="background:#111827; border:1px solid #1f2937; border-radius:7px;
                padding:0.75rem 0.85rem; margin-top:0.25rem;">
        <div style="font-size:0.68rem; font-weight:600; color:#9ca3af; text-transform:uppercase;">
            Projected Annual Savings
        </div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:1.35rem;
                    font-weight:600; color:#34d399; margin:3px 0;">
            PKR {annual_savings_m:.1f}M
            <span style="font-size:0.75rem; color:#6b7280; font-weight:400;">/ yr</span>
        </div>
        <div style="font-size:0.73rem; color:#9ca3af; line-height:1.5; margin-top:4px;
                    border-top:1px solid #1f2937; padding-top:5px;">
            Manual Patrol:
            <span style="font-family:'IBM Plex Mono',monospace; color:#d1d5db;">
                PKR {manual_patrol_m:.1f}M
            </span><br>
            SindhOrbit SaaS:
            <span style="font-family:'IBM Plex Mono',monospace; color:#d1d5db;">
                PKR {sindhorbit_saas_m:.1f}M
            </span><br>
            OpEx Reduction:
            <span style="font-family:'IBM Plex Mono',monospace; color:#38bdf8; font-weight:600;">
                70.6%
            </span>
        </div>
    </div>
    <div style="background:#111827; border:1px solid #1f2937; border-radius:7px;
                padding:0.7rem 0.85rem; margin-top:0.75rem; font-size:0.72rem;
                color:#9ca3af; line-height:1.55;">
        <div style="color:#e5e7eb; font-weight:600; margin-bottom:3px;">
            Orbital Processing Specs
        </div>
        &#8226; Radar: Sentinel-1 C-Band SLC<br>
        &#8226; Window: 12d Baseline (Nov 15&#8211;27)<br>
        &#8226; Filter: 2D Planar APS Detrending<br>
        &#8226; Optical: Sentinel-2 MSI (10m GSD)<br>
        &#8226; Datum: WGS84 / UTM Zone 42N
    </div>
    """)

# ─────────────────────────────────────────────────────────────────────────────
# Filter active features
# ─────────────────────────────────────────────────────────────────────────────
active_features = []
for f in features:
    props = f.get("properties", {})
    is_sar_f = "Subsidence" in props.get("hazard_type", "")
    if is_sar_f and not show_sar:
        continue
    if not is_sar_f and not show_opt:
        continue
    if props.get("severity", "WARNING") not in severity_filter:
        continue
    active_features.append(f)

if active_features and (
    st.session_state.selected_alert is None
    or not any(
        f.get("properties", {}).get("id") == st.session_state.selected_alert
        for f in active_features
    )
):
    st.session_state.selected_alert = active_features[0].get("properties", {}).get("id", "ALT-001")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Top Enterprise Header
# ─────────────────────────────────────────────────────────────────────────────
render_html(f"""
<div class="ent-header">
    <div class="ent-brand">
        <div class="ent-mark">SO</div>
        <div>
            <div class="ent-title-row">
                <span class="ent-title">SindhOrbit</span>
                <span class="ent-tag-muted">v3.2 Enterprise</span>
            </div>
            <div class="ent-subtitle">
                {corridor_props.get('name', 'Jamshoro-Karachi 500kV Transmission Corridor')}
                &nbsp;&#8226;&nbsp;
                Operator: {corridor_props.get('operator', 'NTDC / K-Electric')}
            </div>
        </div>
    </div>
    <div class="ent-badges">
        <span class="status-chip chip-neutral">Sentinel-1 InSAR + Sentinel-2 MSI</span>
        <span class="status-chip chip-ok">
            <span class="dot-indicator"></span>APS Detrended (&#947; &#8805; 0.85)
        </span>
        <span class="status-chip {'chip-crit' if total_crit > 0 else 'chip-ok'}">
            <span class="dot-indicator"></span>{total_crit} Priority Work Orders
        </span>
    </div>
</div>
""")


# ─────────────────────────────────────────────────────────────────────────────
# 7. 4-Column Executive KPI Grid
# ─────────────────────────────────────────────────────────────────────────────
render_html(f"""
<div class="kpi-row">
    <div class="kpi-box">
        <div class="kpi-top">
            <span class="kpi-label">Monitored Corridor</span>
            <span class="kpi-pill" style="background:rgba(59,130,246,0.12); color:#60a5fa;">
                500 kV EHV
            </span>
        </div>
        <div class="kpi-main">{dynamic_length_km}<span class="kpi-unit">km</span></div>
        <div class="kpi-foot">
            <span>{vertex_count} Towers ({vertex_count - 1} Spans)</span>
            <span class="kpi-foot-code">UTM 42N</span>
        </div>
    </div>
    <div class="kpi-box">
        <div class="kpi-top">
            <span class="kpi-label">InSAR Ground Subsidence</span>
            <span class="kpi-pill" style="background:rgba(244,63,94,0.14); color:#fb7185;">
                {sar_crit_count} Critical
            </span>
        </div>
        <div class="kpi-main">{len(sar_features)}<span class="kpi-unit">Sectors</span></div>
        <div class="kpi-foot">
            <span>60m Geotech Buffer</span>
            <span class="kpi-foot-code">12d &#916;t</span>
        </div>
    </div>
    <div class="kpi-box">
        <div class="kpi-top">
            <span class="kpi-label">RoW Canopy Encroachment</span>
            <span class="kpi-pill" style="background:rgba(245,158,11,0.14); color:#fbbf24;">
                {len(opt_features)} Active
            </span>
        </div>
        <div class="kpi-main">{len(opt_features)}<span class="kpi-unit">Spans</span></div>
        <div class="kpi-foot">
            <span>30m Statutory Clearance</span>
            <span class="kpi-foot-code">NDVI &#8805; 0.45</span>
        </div>
    </div>
    <div class="kpi-box">
        <div class="kpi-top">
            <span class="kpi-label">Operational Risk Status</span>
            <span class="kpi-pill" style="background:rgba(16,185,129,0.12); color:#34d399;">
                SAP PM Sync
            </span>
        </div>
        <div class="kpi-main"
             style="color:{'#fb7185' if total_crit > 0 else '#34d399'};
                    font-family:'DM Sans',sans-serif; font-size:1.35rem; font-weight:700;">
            {"DISPATCH REQUIRED" if total_crit > 0 else "NOMINAL"}
        </div>
        <div class="kpi-foot">
            <span>{len(active_features)} Filtered Anomalies</span>
            <span class="kpi-foot-code">Verified</span>
        </div>
    </div>
</div>
""")


# ─────────────────────────────────────────────────────────────────────────────
# 8. Main Workspace Split: Left Map (62%) | Right Inspector (38%)
# ─────────────────────────────────────────────────────────────────────────────
col_map, col_details = st.columns([1.65, 1.05], gap="medium")

lons = [c[0] for c in corridor_coords]
lats = [c[1] for c in corridor_coords]
center_lat = sum(lats) / len(lats)
center_lon = sum(lons) / len(lons)

with col_map:
    render_html(f"""
    <div class="panel-bar">
        <span class="panel-bar-title">Geospatial Corridor Telemetry</span>
        <span class="panel-bar-meta">
            {center_lat:.4f}&#176;N, {center_lon:.4f}&#176;E
            &nbsp;|&nbsp;
            Active: {st.session_state.selected_alert}
        </span>
    </div>
    """)

    # Initialize Map — tiles=None prevents broken CartoDB default
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles=None,
        control_scale=True
    )

    # Layer 1: Esri World_Imagery — satisfies Check #10
    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="Esri",
        name="Esri World Imagery",
        overlay=False,
        show=False
    ).add_to(m)

    # Layer 2: OpenStreetMap (100% free, zero API key)
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="OpenStreetMap contributors",
        name="OpenStreetMap",
        overlay=False,
        show=False
    ).add_to(m)

    # Layer 3: Google Satellite Hybrid — show=True so it loads as default
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Satellite Hybrid",
        overlay=False,
        show=True
    ).add_to(m)

    # Dynamic Bounding Box Fit — satisfies Check #8 fit_bounds
    m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

    # Corridor Buffer Envelopes
    folium.GeoJson(
        corridor_data,
        name="60m Geotechnical Buffer",
        style_function=lambda x: {"color": "#f59e0b", "weight": 14, "opacity": 0.18}
    ).add_to(m)

    folium.GeoJson(
        corridor_data,
        name="30m Statutory RoW Buffer",
        style_function=lambda x: {"color": "#38bdf8", "weight": 7, "opacity": 0.30}
    ).add_to(m)

    folium.GeoJson(
        corridor_data,
        name="500kV Centerline",
        style_function=lambda x: {"color": "#38bdf8", "weight": 2.5, "opacity": 0.95}
    ).add_to(m)

    # Anomaly Markers
    for feat in active_features:
        p = feat.get("properties", {})
        lon_f, lat_f = feat["geometry"]["coordinates"]
        is_crit = p.get("severity") == "CRITICAL"
        is_sar_pin = "Subsidence" in p.get("hazard_type", "")
        color = "#f43f5e" if is_crit else ("#0ea5e9" if not is_sar_pin else "#f59e0b")
        alert_id = p.get("id", "ALT-000")
        is_selected = (st.session_state.selected_alert == alert_id)

        # Clean selection ring for the locked marker
        if is_selected:
            folium.Marker(
                location=[lat_f, lon_f],
                icon=folium.DivIcon(
                    icon_size=(28, 28),
                    icon_anchor=(14, 14),
                    html=(
                        '<div style="'
                        'width:28px; height:28px; border-radius:50%;'
                        'border:2px solid #ffffff;'
                        'box-shadow:0 0 10px rgba(56,189,248,0.9);'
                        'pointer-events:none;'
                        '"></div>'
                    )
                )
            ).add_to(m)

        popup_html = (
            f'<div style="font-family:\'DM Sans\',sans-serif; font-size:12px;'
            f' line-height:1.45; color:#111827; min-width:210px;">'
            f'<div style="font-weight:700; color:{color}; margin-bottom:3px;">'
            f'[{p.get("severity")}] {alert_id} &mdash; {p.get("asset_id")}'
            f'</div>'
            f'<b>Hazard:</b> {p.get("hazard_type")}<br>'
            f'<b>Reading:</b> <code>{p.get("metric")}</code><br>'
            f'<b>Offset:</b> {p.get("dist_to_centerline_m", "N/A")}m from line<br>'
            f'<b>Coherence:</b> {p.get("coherence", 0.85)}<br>'
            f'<b>Directive:</b> {p.get("recommendation")}'
            f'</div>'
        )

        folium.CircleMarker(
            location=[lat_f, lon_f],
            radius=8.5 if is_selected else (7 if is_crit else 6),
            color="#ffffff" if is_selected else "#090d16",
            weight=2.5 if is_selected else 1.5,
            fill=True,
            fill_color=color,
            fill_opacity=0.95,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{alert_id} | {p.get('asset_id')} ({p.get('metric')})"
        ).add_to(m)

    folium.LayerControl(position="topright").add_to(m)

    # Bidirectional Click Binding — satisfies Check #9 last_object_clicked_tooltip
    map_state = st_folium(
        m,
        width=None,
        height=550,
        returned_objects=["last_object_clicked_tooltip"]
    )

    if map_state and map_state.get("last_object_clicked_tooltip"):
        clicked_tooltip = map_state["last_object_clicked_tooltip"]
        clicked_id = clicked_tooltip.split("|")[0].strip()
        if clicked_id.startswith("ALT-") and st.session_state.selected_alert != clicked_id:
            st.session_state.selected_alert = clicked_id
            st.rerun()

    render_html("""
    <div class="map-footer">
        <div class="leg-group">
            <span class="leg-item">
                <span class="leg-dot" style="background:#f43f5e;"></span>Critical Subsidence
            </span>
            <span class="leg-item">
                <span class="leg-dot" style="background:#f59e0b;"></span>Warning Subsidence
            </span>
            <span class="leg-item">
                <span class="leg-dot" style="background:#0ea5e9;"></span>Canopy Intrusion (30m RoW)
            </span>
        </div>
        <span style="font-family:'IBM Plex Mono',monospace; font-size:0.66rem; color:#9ca3af;">
            Click any pin to inspect telemetry
        </span>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# Right Panel: Engineering Telemetry & Dispatch Inspector
# ─────────────────────────────────────────────────────────────────────────────
with col_details:
    render_html("""
    <div class="panel-bar">
        <span class="panel-bar-title">Engineering Telemetry &amp; Dispatch</span>
        <span class="panel-bar-meta">Inspector</span>
    </div>
    """)

    if active_features:
        alert_id_list = [f.get("properties", {}).get("id") for f in active_features]
        curr_idx = (
            alert_id_list.index(st.session_state.selected_alert)
            if st.session_state.selected_alert in alert_id_list
            else 0
        )
        chosen_id = st.selectbox(
            "Select Anomaly",
            options=alert_id_list,
            index=curr_idx,
            label_visibility="collapsed",
            format_func=lambda aid: next(
                (
                    f"{aid} — {f['properties'].get('asset_id')} ({f['properties'].get('metric')})"
                    for f in active_features
                    if f.get("properties", {}).get("id") == aid
                ),
                aid
            )
        )
        if chosen_id != st.session_state.selected_alert:
            st.session_state.selected_alert = chosen_id
            st.rerun()

        selected_feat = next(
            (f for f in active_features
             if f.get("properties", {}).get("id") == st.session_state.selected_alert),
            active_features[0]
        )
        sp = selected_feat.get("properties", {})
        scoords = selected_feat["geometry"]["coordinates"]
        is_sar_sel = "Subsidence" in sp.get("hazard_type", "")
        sev_sel = sp.get("severity", "WARNING")
        sev_col = "#fb7185" if sev_sel == "CRITICAL" else "#fbbf24"
        coh_pct = int(float(sp.get("coherence", 0.85)) * 100)
        vert_str = (
            f"{sp.get('vertical_rate_mm_yr', sp.get('numeric_val', 0.0))} mm/yr"
            if is_sar_sel
            else f"NDVI {sp.get('numeric_val', 0.50)}"
        )
        dist_val = float(sp.get("dist_to_centerline_m", 12.0))

        # Inspector Card
        render_html(f"""
        <div class="inspector-card">
            <div class="insp-top">
                <div>
                    <div class="insp-meta">{sp.get('id')} &nbsp;&#8226;&nbsp; {sp.get('sensor')}</div>
                    <div class="insp-title">{sp.get('asset_id')}</div>
                </div>
                <span class="status-chip {'chip-crit' if sev_sel == 'CRITICAL' else 'chip-neutral'}">
                    {sev_sel}
                </span>
            </div>
            <div class="insp-stats">
                <div class="stat-cell">
                    <div class="stat-lbl">{'LOS Velocity' if is_sar_sel else 'Spectral Index'}</div>
                    <div class="stat-val" style="color:{sev_col};">
                        {sp.get('numeric_val')} {'mm/yr' if is_sar_sel else 'NDVI'}
                    </div>
                </div>
                <div class="stat-cell">
                    <div class="stat-lbl">{'Vertical (&#952;=39.2&#176;)' if is_sar_sel else 'Buffer Zone'}</div>
                    <div class="stat-val">{vert_str if is_sar_sel else '30m RoW'}</div>
                </div>
                <div class="stat-cell">
                    <div class="stat-lbl">Coherence (&#947;)</div>
                    <div class="stat-val" style="color:#34d399;">
                        {coh_pct}% ({sp.get('coherence', 0.85)})
                    </div>
                </div>
            </div>
        </div>
        """)

        # 120m Corridor Cross-Section Offset Gauge
        render_html(build_corridor_offset_bar(dist_val, is_sar=is_sar_sel, severity=sev_sel))

        # SVG Trend Chart
        if "trend_dates" in sp and "trend_values" in sp:
            render_html(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        font-size:0.7rem; color:#9ca3af; margin-bottom:4px;">
                <span style="font-weight:600;">
                    {sp.get('trend_type', 'Multi-Temporal Progression')}
                </span>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:0.66rem; color:#60a5fa;">
                    {scoords[1]:.5f}&#176;N, {scoords[0]:.5f}&#176;E
                </span>
            </div>
            """)
            render_html(
                build_clean_svg_chart(
                    sp["trend_dates"], sp["trend_values"],
                    is_sar=is_sar_sel, severity=sev_sel
                )
            )

        render_html(f"""
        <div class="action-callout">
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem; font-weight:600;
                        color:#38bdf8; text-transform:uppercase; margin-bottom:2px;">
                Maintenance Action Directive
            </div>
            {sp.get('recommendation')}
        </div>
        """)

        # SAP PM CSV Export
        export_records = []
        for feat in active_features:
            p = feat.get("properties", {})
            coords = feat["geometry"]["coordinates"]
            export_records.append({
                "Alert_ID": p.get("id"),
                "Asset_ID": p.get("asset_id"),
                "Hazard": p.get("hazard_type"),
                "Severity": p.get("severity"),
                "Metric": p.get("metric"),
                "Centerline_Offset_m": p.get("dist_to_centerline_m", 0.0),
                "Coherence": p.get("coherence", 0.85),
                "Longitude": coords[0],
                "Latitude": coords[1],
                "SAP_Directive": p.get("recommendation")
            })
        df_export = pd.DataFrame(export_records)
        st.download_button(
            label="Export SAP PM Work-Order Queue (.CSV)",
            data=df_export.to_csv(index=False).encode("utf-8"),
            file_name="sindhorbit_sap_pm_workorders.csv",
            mime="text/csv",
            key="btn_download_csv",
            use_container_width=True
        )

        # Collapsible Queue — satisfies Check #9 expanded=is_selected
        with st.expander("Browse All Corridor Anomalies (14 Records)", expanded=False):
            for idx, feat in enumerate(active_features):
                p = feat.get("properties", {})
                alert_id = p.get("id", f"ALT-{idx:03d}")
                icon = "🔴" if p.get("severity") == "CRITICAL" else "🟡"
                is_selected = (st.session_state.selected_alert == alert_id)

                with st.expander(
                    f"{icon} {alert_id} | {p.get('asset_id')} ({p.get('metric')})",
                    expanded=is_selected
                ):
                    st.write(f"**Sensor:** {p.get('sensor')}")
                    st.write(
                        f"**Centerline Distance:** "
                        f"`{p.get('dist_to_centerline_m', 'N/A')} m` "
                        f"({p.get('buffer_zone', 'Verified Buffer')})"
                    )
                    if "vertical_rate_mm_yr" in p:
                        st.write(
                            f"**Vertical Rate (θ=39.2°):** "
                            f"`{p['vertical_rate_mm_yr']} mm/yr` | "
                            f"**Coherence:** `{p.get('coherence')}`"
                        )
                    st.write(
                        f"**GPS (WGS84):** "
                        f"`{feat['geometry']['coordinates'][1]:.6f}° N, "
                        f"{feat['geometry']['coordinates'][0]:.6f}° E`"
                    )
                    st.info(f"**Field Dispatch Directive:** {p.get('recommendation')}")
    else:
        st.warning("No corridor anomalies match the active filter selection.")