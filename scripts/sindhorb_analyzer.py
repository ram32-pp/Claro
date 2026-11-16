import os
import glob
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import matplotlib.pyplot as plt
from shapely.geometry import Point

# ==========================================
# 1. AUTOMATIC FILE DISCOVERY
# ==========================================
def find_file_by_pattern(pattern):
    matches = glob.glob(pattern)
    if not matches:
        return None
    return matches[0]

# Auto-detect GeoJSON vector path
geojson_file = find_file_by_pattern("*.geojson")
if not geojson_file:
    raise FileNotFoundError("No .geojson file found in the working directory.")

# Auto-detect InSAR GeoTIFF rasters
phase_file = find_file_by_pattern("*_unw_phase.tif")
corr_file = find_file_by_pattern("*_corr.tif")
water_file = find_file_by_pattern("*_water_mask.tif")

if not (phase_file and corr_file):
    raise FileNotFoundError("Could not find both *_unw_phase.tif and *_corr.tif in the directory.")

print("=" * 60)
print(f" Loaded Vector:    {os.path.basename(geojson_file)}")
print(f" Loaded Phase Map: {os.path.basename(phase_file)}")
print(f" Loaded Coherence: {os.path.basename(corr_file)}")
if water_file:
    print(f" Loaded Water Mask:{os.path.basename(water_file)}")
print("=" * 60)

# ==========================================
# 2. SPATIAL BUFFERING (50m Right-of-Way)
# ==========================================
corridor_gdf = gpd.read_file(geojson_file)
if corridor_gdf.crs != "EPSG:4326":
    corridor_gdf = corridor_gdf.to_crs("EPSG:4326")

# Project to meters to generate an accurate 50m corridor buffer
corridor_m = corridor_gdf.to_crs(epsg=3857)
buffer_m = corridor_m.buffer(50) 
buffer_gdf = gpd.GeoDataFrame(geometry=buffer_m, crs="EPSG:3857").to_crs("EPSG:4326")
centerline = corridor_m.geometry.iloc[0]

# ==========================================
# 3. RASTER CLIPPING FUNCTION
# ==========================================
def clip_raster(filepath, poly_gdf):
    with rasterio.open(filepath) as src:
        if poly_gdf.crs != src.crs:
            poly_gdf = poly_gdf.to_crs(src.crs)
        img, transform = mask(src, poly_gdf.geometry, crop=True)
        meta = src.meta
    return img[0].astype(float), transform, meta

print("\nProcessing spatial clipping across corridor...")
phase_img, transform, meta = clip_raster(phase_file, buffer_gdf)
corr_img, _, _ = clip_raster(corr_file, buffer_gdf)

# ==========================================
# 4. FILTERING NOISE & ISOLATING PYLONS
# ==========================================
# Filter pixels: Valid data & Coherence >= 0.6 (isolates steel structures and firm soil)
valid_mask = (phase_img != meta['nodata']) & (corr_img >= 0.6)

# Integrate water mask if present
if water_file:
    water_img, _, _ = clip_raster(water_file, buffer_gdf)
    # Filter out water pixels (assuming non-zero values represent water)
    valid_mask = valid_mask & (water_img == 0)

rows, cols = np.where(valid_mask)
valid_phase = phase_img[valid_mask]

# Convert Phase (radians) -> Line-of-Sight Displacement (mm)
# Sentinel-1 C-Band Wavelength = 55.465 mm
disp_mm = (valid_phase * 55.465) / (4 * np.pi)

print(f"Isolated {len(disp_mm)} high-coherence infrastructure scatterers.")

# ==========================================
# 5. ROUTE STATIONING (Km Distance Calculation)
# ==========================================
distances_km = []
xs, ys = rasterio.transform.xy(transform, rows, cols)
pts = gpd.GeoSeries([Point(x, y) for x, y in zip(xs, ys)], crs=meta['crs'])
pts_m = pts.to_crs(epsg=3857)

for pt in pts_m:
    dist_m = centerline.project(pt)
    distances_km.append(dist_m / 1000.0)

distances_km = np.array(distances_km)

# Sort points chronologically along route distance
sort_idx = np.argsort(distances_km)
distances_km = distances_km[sort_idx]
disp_mm = disp_mm[sort_idx]

# ==========================================
# 6. EXECUTIVE SUMMARY & PLOT GENERATION
# ==========================================
max_sub = np.min(disp_mm) if len(disp_mm) > 0 else 0
max_up = np.max(disp_mm) if len(disp_mm) > 0 else 0
mean_disp = np.mean(disp_mm) if len(disp_mm) > 0 else 0

print("\n" + "=" * 60)
print(" CLARO: K-ELECTRIC DHABEJI CORRIDOR DIAGNOSTIC SUMMARY")
print("=" * 60)
print(f"Target Line Span:          {np.max(distances_km):.2f} km")
print(f"Identified Tower Points:   {len(disp_mm)}")
print(f"Max Asset Subsidence:      {max_sub:.2f} mm")
print(f"Max Asset Uplift:          {max_up:.2f} mm")
print(f"Average Corridor Motion:   {mean_disp:.2f} mm")
print("=" * 60)

# Generate Scatter Plot
fig, ax = plt.subplots(figsize=(11, 4.5), dpi=300)
sc = ax.scatter(distances_km, disp_mm, s=18, c=disp_mm, cmap='coolwarm_r', alpha=0.85, edgecolor='black', linewidth=0.3)

# Add threshold lines
ax.axhline(0, color='black', linestyle='-', linewidth=0.8)
ax.axhline(-5.0, color='darkorange', linestyle='--', linewidth=1.2, label='Warning Threshold (-5 mm)')
ax.axhline(-10.0, color='red', linestyle='--', linewidth=1.2, label='Critical Subsidence (-10 mm)')

ax.set_title("Dhabeji–Bin Qasim 132kV Infrastructure Stability Profile", fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel("Distance along Transmission Line from Dhabeji Grid (km)", fontsize=10, fontweight='bold')
ax.set_ylabel("Ground / Pylon Displacement (mm)", fontsize=10, fontweight='bold')

ax.set_xlim(0, max(distances_km) + 0.5 if len(distances_km) > 0 else 25)
ax.set_ylim(min(-15, max_sub - 2), max(10, max_up + 2))
ax.grid(True, linestyle=':', alpha=0.5)
ax.legend(loc='lower left', frameon=True)
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label("Displacement (mm)", fontsize=9)

plt.tight_layout()
output_chart = "KE_Dhabeji_Diagnostic_Audit.png"
plt.savefig(output_chart)
print(f"\nSuccess: Exported audit graph to '{output_chart}'")