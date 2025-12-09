import ee
import streamlit as st
import geemap.foliumap as geemap
import pandas as pd
import plotly.express as px

# ------------------------------------------------
# INIT EARTH ENGINE
# ------------------------------------------------
try:
    ee.Initialize(project='estuaria')
except:
    ee.Authenticate()
    ee.Initialize(project='estuaria')

# ------------------------------------------------
# PAGE HEADER
# ------------------------------------------------
st.title("💧 Water Quality & Turbidity – UCUP Dashboard")

st.markdown(
    """
    Modul ini menampilkan **NDWI (indikator keberadaan air)** dan 
    **NDTI (turbiditas/kekeruhan)** untuk Estuari Muara Angke (2020–2024).

    - **NDWI** → mendeteksi air dan area basah  
    - **NDTI** → mengukur tingkat kekeruhan air  
    """
)

# ------------------------------------------------
# AOI
# ------------------------------------------------
AOI = ee.Geometry.Polygon([[
    [106.7535685, -6.1066100],
    [106.7771719, -6.1066100],
    [106.7771719, -6.0886875],
    [106.7535685, -6.0886875]
]])

# ------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------
st.sidebar.header("⚙️ Pengaturan Turbiditas")

year = st.sidebar.selectbox("Pilih Tahun", [2020, 2021, 2022, 2023, 2024], index=4)

cloud_thresh = st.sidebar.slider(
    "Cloud Max (%)",
    min_value=0, max_value=30, value=10, step=1
)

layer_type = st.sidebar.radio(
    "Pilih Layer Tampilan",
    ["NDWI (Air)", "NDTI (Turbiditas)"],
    index=1
)

# ------------------------------------------------
# FUNGSI AMBIL NDWI + NDTI PER TAHUN
# ------------------------------------------------
def get_ndwi_ndti(year, cloud_limit=10):

    start = f"{year}-01-01"
    end   = f"{year}-12-31"

    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(AOI)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_limit))
        .median()
        .clip(AOI)
        .select(["B3", "B4", "B8"])  # Green, Red, NIR
    )

    green = s2.select("B3")
    red   = s2.select("B4")
    nir   = s2.select("B8")

    # NDWI
    ndwi = green.subtract(nir).divide(green.add(nir).add(1e-6)).rename("NDWI")

    # Mask air
    water = ndwi.gt(0).rename("watermask")

    # NDTI
    ndti = red.subtract(green).divide(red.add(green).add(1e-6)).rename("NDTI")

    # Clip hanya area air
    ndti_water = ndti.updateMask(water).clip(AOI)

    return ndwi, ndti_water, water

# ------------------------------------------------
# HITUNG CITRA PER TAHUN
# ------------------------------------------------
ndwi_img, ndti_img, watermask = get_ndwi_ndti(year, cloud_limit=cloud_thresh)

# ------------------------------------------------
# FUNGSI HITUNG STATISTIK
# ------------------------------------------------
def compute_stats(image):
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            reducer2=ee.Reducer.stdDev(), sharedInputs=True
        ),
        geometry=AOI,
        scale=10,
        maxPixels=1e13
    )

    try:
        mean = float(ee.Number(stats.get("mean")).getInfo())
    except:
        mean = None

    try:
        std = float(ee.Number(stats.get("stdDev")).getInfo())
    except:
        std = None

    return mean, std

mean_ndwi, std_ndwi = compute_stats(ndwi_img)
mean_ndti, std_ndti = compute_stats(ndti_img)

# ------------------------------------------------
# SUMMARY CARDS
# ------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "📏 Rata-rata NDWI",
        f"{mean_ndwi:.3f}" if mean_ndwi is not None else "N/A",
        help="Semakin tinggi → semakin basah / area berair."
    )

with col2:
    st.metric(
        "🌫️ Rata-rata NDTI (Turbiditas)",
        f"{mean_ndti:.3f}" if mean_ndti is not None else "N/A",
        help="Semakin tinggi → semakin keruh air."
    )

st.markdown("---")

# ------------------------------------------------
# PETA INTERAKTIF
# ------------------------------------------------
st.subheader(f"🗺️ Peta NDWI / NDTI Tahun {year}")

m = geemap.Map(center=[-6.098, 106.765], zoom=15)
m.add_basemap("CartoDB.DarkMatter")

# AOI outline
m.addLayer(AOI, {"color": "yellow"}, "AOI")

# Visual style
ndwi_vis = {"min": -0.5, "max": 0.5, "palette": ["red", "white", "blue"]}
ndti_vis = {"min": -0.5, "max": 0.5, "palette": ["blue", "green", "yellow", "orange", "red"]}

if layer_type.startswith("NDWI"):
    m.addLayer(ndwi_img, ndwi_vis, f"NDWI {year}")
    legend = {"Dry": "red", "Neutral": "white", "Wet": "blue"}
else:
    m.addLayer(ndti_img, ndti_vis, f"NDTI {year}")
    legend = {"Low Turbidity": "blue", "Medium": "yellow", "High": "red"}

m.add_legend(title=layer_type, legend_dict=legend)
m.to_streamlit(height=500)

# ------------------------------------------------
# HISTOGRAM NDTI
# ------------------------------------------------
st.subheader(f"📊 Histogram NDTI (Turbiditas) – {year}")

hist_dict = ndti_img.reduceRegion(
    reducer=ee.Reducer.histogram(maxBuckets=30),
    geometry=AOI,
    scale=10,
    maxPixels=1e13
)

try:
    hist = ee.Dictionary(hist_dict.get("NDTI")).getInfo()
    df = pd.DataFrame({"NDTI": hist["bucketMeans"], "Count": hist["histogram"]})

    fig = px.bar(
        df,
        x="NDTI",
        y="Count",
        title=f"Distribusi Turbiditas (NDTI) – {year}",
        labels={"NDTI": "Nilai NDTI", "Count": "Jumlah Piksel"}
    )
    st.plotly_chart(fig, use_container_width=True)

except:
    st.info("Histogram tidak dapat dihitung (kemungkinan data air sedikit).")
