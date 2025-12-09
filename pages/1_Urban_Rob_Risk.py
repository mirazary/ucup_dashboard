import streamlit as st
import ee
import geemap.foliumap as geemap

# =========================================================
# INIT
# =========================================================
try:
    ee.Initialize(project="estuaria")
except:
    ee.Authenticate()
    ee.Initialize(project="estuaria")

st.title("🌊 Flood Hazard Index – UCUP Dashboard")

# =========================================================
# AOI
# =========================================================
aoi = ee.Geometry.Polygon([[
    [106.7535685, -6.1066100],
    [106.7771719, -6.1066100],
    [106.7771719, -6.0886875],
    [106.7535685, -6.0886875]
]])

years = [2020, 2021, 2022, 2023, 2024]

selected_year = st.sidebar.selectbox("Pilih Tahun (Landsat)", years)

# =========================================================
# LOAD DATASETS
# =========================================================
gsw = ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
srtm = ee.Image("USGS/SRTMGL1_003")
l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")

# rainbow palette
rainbow = ["blue", "cyan", "green", "yellow", "red"]

# =========================================================
# CLOUD MASK FOR LANDSAT 8
# =========================================================
def cloudMask(image):
    qa = image.select("QA_PIXEL")
    dilated = 1 << 1
    cirrus = 1 << 2
    cloud = 1 << 3
    shadow = 1 << 4

    mask = (qa.bitwiseAnd(dilated).eq(0)
            .And(qa.bitwiseAnd(cirrus).eq(0))
            .And(qa.bitwiseAnd(cloud).eq(0))
            .And(qa.bitwiseAnd(shadow).eq(0)))

    return (image
            .select(["SR_B.*"], ["B1","B2","B3","B4","B5","B6","B7"])
            .multiply(0.0000275).add(-0.2)
            .updateMask(mask))

# =========================================================
# GENERATE FLOOD HAZARD
# =========================================================
def compute_flood_hazard():

    # 1️⃣ Water Occurrence
    water = gsw.select("occurrence").clip(aoi)

    # Permanent water
    permanent = water.gt(80)

    # 2️⃣ Distance from water
    distance = permanent.fastDistanceTransform().divide(30).clip(aoi)

    only_distance = distance.updateMask(distance.neq(0).And(srtm.mask()))

    # 3️⃣ Distance score
    distanceScore = (only_distance
        .where(only_distance.gt(4000), 1)
        .where(only_distance.gt(3000).And(only_distance.lte(4000)), 2)
        .where(only_distance.gt(2000).And(only_distance.lte(3000)), 3)
        .where(only_distance.gt(1000).And(only_distance.lte(2000)), 4)
        .where(only_distance.lte(1000), 5))

    # 4️⃣ Elevation Score
    elev = srtm.clip(aoi)
    elevScore = (elev.updateMask(distance.neq(0))
        .where(elev.gt(20), 1)
        .where(elev.gt(15).And(elev.lte(20)), 2)
        .where(elev.gt(10).And(elev.lte(15)), 3)
        .where(elev.gt(5).And(elev.lte(10)), 4)
        .where(elev.lte(5), 5))

    # 5️⃣ TPI Score
    tpi = elev.subtract(elev.focalMean(5))
    topoScore = (tpi.updateMask(distance.neq(0))
        .where(tpi.gt(0), 1)
        .where(tpi.gt(-2).And(tpi.lte(0)), 2)
        .where(tpi.gt(-4).And(tpi.lte(-2)), 3)
        .where(tpi.gt(-6).And(tpi.lte(-4)), 4)
        .where(tpi.lte(-8), 5))

    # 6️⃣ Landsat 8 NDVI + NDWI (tahun sesuai pilihan)
    landsat = (l8.filterBounds(aoi)
                .filterDate(f"{selected_year}-01-01", f"{selected_year}-12-31")
                .map(cloudMask)
                .median()
                .clip(aoi))

    RED = landsat.select("B4")
    NIR = landsat.select("B5")
    GREEN = landsat.select("B3")

    ndvi = (NIR.subtract(RED)).divide(NIR.add(RED)).rename("NDVI")
    ndwi = (GREEN.subtract(NIR)).divide(GREEN.add(NIR)).rename("NDWI")

    # Vegetation Score
    vegScore = (ndvi.updateMask(distance.neq(0))
        .where(ndvi.gt(0.8), 1)
        .where(ndvi.gt(0.6).And(ndvi.lte(0.8)), 2)
        .where(ndvi.gt(0.4).And(ndvi.lte(0.6)), 3)
        .where(ndvi.gt(0.2).And(ndvi.lte(0.4)), 4)
        .where(ndvi.lte(0.2), 5))

    # Wetness Score
    wetScore = (ndwi.updateMask(distance.neq(0))
        .where(ndwi.gt(0.6), 5)
        .where(ndwi.gt(0.2).And(ndwi.lte(0.6)), 4)
        .where(ndwi.gt(-0.2).And(ndwi.lte(0.2)), 3)
        .where(ndwi.gt(-0.6).And(ndwi.lte(-0.2)), 2)
        .where(ndwi.lte(-0.6), 1))

    # 7️⃣ Flood Hazard Total
    floodHazard = (distanceScore
        .add(topoScore)
        .add(vegScore)
        .add(wetScore)
        .add(elevScore)
        .rename("FHI"))

    # Final Score (1–5)
    floodScore = (floodHazard
        .where(floodHazard.gt(15), 5)
        .where(floodHazard.gt(10).And(floodHazard.lte(15)), 4)
        .where(floodHazard.gt(5).And(floodHazard.lte(10)), 3)
        .where(floodHazard.gt(0).And(floodHazard.lte(5)), 2)
        .where(floodHazard.lte(0), 1))

    return {
        "distance": only_distance,
        "distanceScore": distanceScore,
        "ndvi": ndvi,
        "ndwi": ndwi,
        "vegScore": vegScore,
        "wetScore": wetScore,
        "tpi": tpi,
        "topoScore": topoScore,
        "elevScore": elevScore,
        "floodHazard": floodHazard,
        "floodScore": floodScore
    }


# =========================================================
# GENERATE MAP
# =========================================================
result = compute_flood_hazard()

m = geemap.Map(center=[-6.098, 106.765], zoom=15)

# Layer selector
layer_choice = st.sidebar.radio("Tampilkan Layer:", [
    "Flood Hazard Final Score (1–5)",
    "Flood Hazard Raw (5–25)",
    "Distance Score",
    "Elevation Score",
    "Topographic Score",
    "Vegetation Score",
    "Wetness Score"
])

if layer_choice == "Flood Hazard Final Score (1–5)":
    m.addLayer(result["floodScore"], {"min":1, "max":5, "palette":rainbow}, "Flood Hazard Score")
elif layer_choice == "Flood Hazard Raw (5–25)":
    m.addLayer(result["floodHazard"], {"min":5, "max":25, "palette":rainbow}, "Flood Hazard Raw")
elif layer_choice == "Distance Score":
    m.addLayer(result["distanceScore"], {"min":1, "max":5, "palette":rainbow}, "Distance Score")
elif layer_choice == "Elevation Score":
    m.addLayer(result["elevScore"], {"min":1, "max":5, "palette":rainbow}, "Elevation Score")
elif layer_choice == "Topographic Score":
    m.addLayer(result["topoScore"], {"min":1, "max":5, "palette":rainbow}, "TPI Score")
elif layer_choice == "Vegetation Score":
    m.addLayer(result["vegScore"], {"min":1, "max":5, "palette":rainbow}, "Vegetation Score")
elif layer_choice == "Wetness Score":
    m.addLayer(result["wetScore"], {"min":1, "max":5, "palette":rainbow}, "Wetness Score")

m.to_streamlit(height=600)

