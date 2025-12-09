import ee
import streamlit as st
import geemap.foliumap as geemap
import pandas as pd
import plotly.express as px
import json
import tempfile
import os

# INIT GEE DARI SERVICE ACCOUNT
@st.cache_resource
def init_ee_service_account():
    try:
        sa_json_str = st.secrets["gee"]["service_account_json"]
        sa_info = json.loads(sa_json_str)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as fp:
            json.dump(sa_info, fp)
            key_file_path = fp.name

        credentials = ee.ServiceAccountCredentials(
            email=sa_info["client_email"],
            key_file=key_file_path,
        )

        ee.Initialize(credentials, project=sa_info["project_id"])
        os.remove(key_file_path)
        return True

    except Exception as e:
        st.error(f"❌ Gagal menginisialisasi Google Earth Engine:\n\n{e}")
        st.stop()

init_ee_service_account()

# PAGE HEADER
st.title("💧 Water Quality & Turbidity")

st.markdown(
    """
    Modul ini menampilkan **NDWI (indikator keberadaan air)** dan 
    **NDTI (turbiditas/kekeruhan)** untuk Estuari Muara Angke (2020–2024).

    - **NDWI** → mendeteksi air  
    - **NDTI** → mengukur tingkat kekeruhan air  
    """
)

# AOI
AOI = ee.Geometry.Polygon([[
    [106.7535685, -6.1066100],
    [106.7771719, -6.1066100],
    [106.7771719, -6.0886875],
    [106.7535685, -6.0886875],
]])

# SIDEBAR FILTERS
st.sidebar.header("⚙️ Pengaturan Turbiditas")

year = st.sidebar.selectbox("Pilih Tahun", [2020, 2021, 2022, 2023, 2024], index=4)

cloud_thresh = st.sidebar.slider(
    "Cloud Max (%)", 0, 30, 10, 1
)

layer_type = st.sidebar.radio(
    "Pilih Layer Tampilan",
    ["NDWI (Air)", "NDTI (Turbiditas)"],
    index=1
)

# AMBIL NDWI & NDTI
def get_ndwi_ndti(year, cloud_limit=10):
    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(AOI)
        .filterDate(f"{year}-01-01", f"{year}-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_limit))
        .median()
        .clip(AOI)
    )

    green = s2.select("B3")
    red   = s2.select("B4")
    nir   = s2.select("B8")

    ndwi = green.subtract(nir).divide(green.add(nir).add(1e-6)).rename("NDWI")

    watermask = ndwi.gt(0).rename("watermask")

    ndti = red.subtract(green).divide(red.add(green).add(1e-6)).rename("NDTI")
    ndti_water = ndti.updateMask(watermask).clip(AOI)

    return ndwi, ndti_water, watermask

ndwi_img, ndti_img, watermask = get_ndwi_ndti(year, cloud_limit=cloud_thresh)

# PETA INTERAKTIF
st.subheader(f"🗺️ Peta NDWI / NDTI – Tahun {year}")

m = geemap.Map(center=[-6.098, 106.765], zoom=15)
m.add_basemap("CartoDB.DarkMatter")
m.addLayer(AOI, {"color": "yellow"}, "AOI")

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

# HISTOGRAM NDTI
st.subheader(f"📊 Histogram NDTI (Turbiditas) – {year}")

hist_dict = ndti_img.reduceRegion(
    reducer=ee.Reducer.histogram(maxBuckets=30),
    geometry=AOI,
    scale=10,
    maxPixels=1e13,
)

try:
    hist = ee.Dictionary(hist_dict.get("NDTI")).getInfo()
    df = pd.DataFrame({"NDTI": hist["bucketMeans"], "Count": hist["histogram"]})

    fig = px.bar(
        df,
        x="NDTI",
        y="Count",
        title=f"Distribusi Turbiditas (NDTI) – {year}",
        labels={"NDTI": "Nilai NDTI", "Count": "Jumlah Piksel"},
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception:
    st.info("Histogram tidak dapat dihitung (kemungkinan data air sedikit).")
