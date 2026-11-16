# scripts/process_optical.py - Dual-Season Phenological Woody Canopy Filter (Sentinel-2 MSI)
"""
Claro Optical Engine:
Implements a Dual-Season Phenological Persistence Filter using Copernicus Sentinel-2 L2A MSI imagery.
By coupling peak arid summer (pre-monsoon, April-June) with peak post-monsoon (August-October),
it separates seasonal agricultural crops (which get harvested to bare soil NDVI < 0.20)
from deep-rooted perennial woody canopy (Prosopis juliflora / Eucalyptus camaldulensis)
encroaching within the 30-meter statutory Right-of-Way (RoW) buffer.
"""
import json
import os
from pathlib import Path

def run_optical_pipeline(corridor_path="data/corridor.geojson", 
                         output_json="data/optical_alerts.geojson", 
                         project_id="project-28bb2462-aed8-43b2-89b"):
    try:
        import ee
    except ImportError:
        print("Notice: earthengine-api not installed in local environment. Run in Google Colab / cloud environment with Earth Engine credentials.")
        return

    # 1. Initialize Google Earth Engine
    print(f"Initializing Earth Engine with project: {project_id}...")
    try:
        ee.Initialize(project=project_id)
    except Exception:
        print("Authenticating Earth Engine session...")
        ee.Authenticate()
        ee.Initialize(project=project_id)

    # 2. Ingest Transmission Corridor & Construct 30m Statutory RoW Buffer
    with open(corridor_path, "r", encoding="utf-8") as f:
        corridor_geo = json.load(f)

    coords = corridor_geo["features"][0]["geometry"]["coordinates"]
    # Ensure 2D [lon, lat] coordinates
    coords_2d = [[round(c[0], 6), round(c[1], 6)] for c in coords]
    ee_line = ee.Geometry.LineString(coords_2d)
    ee_buffer = ee_line.buffer(30.0)

    # 3. Dual-Season Sentinel-2 L2A Image Compositing
    print("Querying Sentinel-2 Harmonized Top-of-Canopy Reflectance...")
    
    # Season 1: Pre-Monsoon Peak Arid Summer (Apr 1 - Jun 15)
    # Seasonal crops are harvested/fallow (NDVI < 0.20); only deep-rooted phreatophytic trees stay green
    s2_dry = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(ee_buffer)
        .filterDate("2026-04-01", "2026-06-15")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 15))
        .median()
        .clip(ee_buffer)
    )
    
    # Season 2: Post-Monsoon Maximum Biomass Surge (Aug 1 - Oct 20)
    # Peak growth phase following summer monsoons
    s2_wet = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(ee_buffer)
        .filterDate("2026-08-01", "2026-10-20")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 15))
        .median()
        .clip(ee_buffer)
    )

    ndvi_dry = s2_dry.normalizedDifference(["B8", "B4"]).rename("NDVI_DRY")
    ndvi_wet = s2_wet.normalizedDifference(["B8", "B4"]).rename("NDVI_WET")

    # 4. Phenological Persistence Condition:
    # Requires NDVI_dry >= 0.35 (persistent green foliage during drought) AND NDVI_wet >= 0.45
    woody_canopy_mask = ndvi_dry.gte(0.35).And(ndvi_wet.gte(0.45))
    zone = woody_canopy_mask.selfMask().toByte().rename("zone")
    combined_image = zone.addBands(ndvi_wet.rename("NDVI"))

    # 5. Extract Vector Encroachments
    print("Vectorizing persistent woody canopy clusters within 30m RoW...")
    vectors = combined_image.reduceToVectors(
        reducer=ee.Reducer.mean(),
        geometry=ee_buffer,
        scale=10,
        geometryType="centroid",
        maxPixels=int(1e8)
    )

    def format_alert(feat):
        mean_val = ee.Number(feat.get("mean"))
        is_crit = mean_val.gt(0.60)
        return feat.set({
            "hazard_type": "Right-of-Way Vegetation Intrusion",
            "severity": ee.Algorithms.If(is_crit, "CRITICAL", "WARNING"),
            "metric": ee.String("NDVI ").cat(mean_val.format("%.2f")).cat(" (Dual-Season Woody Persistent)"),
            "numeric_val": mean_val,
            "coherence": 0.90,
            "buffer_zone": "Inner 30m Statutory RoW",
            "sensor": "Sentinel-2 Multispectral MSI (Dual-Season Woody Filter)",
            "date_detected": "2026-10-20",
            "trend_type": "Multi-Temporal Phenological Woody Canopy Growth",
            "recommendation": ee.Algorithms.If(
                is_crit,
                "Dispatch vegetation clearance crew for urgent pylon conductor Right-of-Way pruning.",
                "Schedule routine trimming during quarterly vegetation maintenance cycle."
            )
        })

    formatted_alerts = vectors.limit(20).map(format_alert)
    geojson_dict = formatted_alerts.getInfo()
    features = geojson_dict.get("features", [])

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(geojson_dict, f, indent=2)

    print(f"SUCCESS: Exported {len(features)} persistent woody canopy alerts to {output_json}.")
    return geojson_dict

if __name__ == "__main__":
    run_optical_pipeline(
        corridor_path="data/corridor.geojson",
        output_json="data/optical_alerts.geojson"
    )
