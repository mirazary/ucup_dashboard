import streamlit as st
import ee
import geemap.foliumap as geemap
import pandas as pd
import plotly.express as px
import json
import tempfile
import os

@st.cache_resource
def init_ee_service_account():
    try:
        # 1. Ambil JSON service account dari secrets
        sa_json_str = st.secrets["gee"]["service_account_json"]
        sa_info = json.loads(sa_json_str)

        # 2. Tulis ke file sementara
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as fp:
            json.dump(sa_info, fp)
            key_file_path = fp.name

        # 3. Buat credentials dari file
        credentials = ee.ServiceAccountCredentials(
            email=sa_info["client_email"],
            key_file=key_file_path,
        )

        # 4. Inisialisasi Earth Engine
        ee.Initialize(credentials, project=sa_info["project_id"])

        # 5. Hapus file sementara
        os.remove(key_file_path)

        return True

    except Exception as e:
        st.error(f"❌ Gagal menginisialisasi Google Earth Engine:\n\n{e}")
        st.stop()

# PANGGIL SEKALI DI AWAL HALAMAN
init_ee_service_account()

st.title("🌿 Mangrove Dashboard")

# AOI MUARA ANGKE
aoi = ee.Geometry.Polygon(
    [
        [
            [106.7535685, -6.1066100],
            [106.7771719, -6.1066100],
            [106.7771719, -6.0886875],
            [106.7535685, -6.0886875],
        ]
    ]
)

# SIDEBAR SETTINGS
st.sidebar.header("⚙️ Pengaturan")

selected_year = st.sidebar.selectbox("Pilih Tahun", [2020, 2021, 2022, 2023, 2024])

min_mvi = st.sidebar.slider("Minimum MVI", 0.0, 5.0, 2.50, 0.01)
max_mvi = st.sidebar.slider("Maximum MVI", 0.0, 25.0, 20.00, 0.01)

show_mvi = st.sidebar.checkbox("Tampilkan Layer MVI", False)

# GET MVI FUNCTION
def get_mvi(year):
    start = f"{year}-05-01"
    end = f"{year}-09-30"

    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .median()
        .clip(aoi)
    )

    green = s2.select("B3")
    nir = s2.select("B8")
    swir1 = s2.select("B11")

    mvi = nir.subtract(green).divide(swir1.subtract(green).add(1e-6)).rename("MVI")

    mask_map = mvi.gte(min_mvi).And(mvi.lte(max_mvi)).selfMask()
    mask_area = mvi.gte(min_mvi).And(mvi.lte(max_mvi)).rename("mask").uint8()

    return mvi, mask_map, mask_area

years = [2020, 2021, 2022, 2023, 2024]

mvi_dict = {}
mask_map_dict = {}
mask_area_dict = {}
area_dict = {}

# CALC AREA FUNCTION
def calc_area(mask):
    area = (
        mask.multiply(ee.Image.pixelArea())
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=aoi,
            scale=10,
            maxPixels=1e13,
        )
        .get("mask")
    )

    if area is None:
        return 0.0

    return ee.Number(area).divide(10000).getInfo()  # m² → ha

# PROCESS ALL YEARS
for yr in years:
    mvi, mask_map, mask_area = get_mvi(yr)
    mvi_dict[yr] = mvi
    mask_map_dict[yr] = mask_map
    mask_area_dict[yr] = mask_area
    area_dict[yr] = calc_area(mask_area)
    
# LOSS & GAIN
loss_mask = mask_area_dict[2020].And(mask_area_dict[2024].Not()).uint8()
gain_mask = mask_area_dict[2024].And(mask_area_dict[2020].Not()).uint8()

loss_area = calc_area(loss_mask)
gain_area = calc_area(gain_mask)

# SIDEBAR SUMMARY
st.sidebar.header("📌 Ringkasan")

st.sidebar.metric("🌿 Luas Mangrove 2020", f"{area_dict[2020]:.2f} ha")
st.sidebar.metric("🌿 Luas Mangrove 2024", f"{area_dict[2024]:.2f} ha")

st.sidebar.metric("🔥 LOSS 2020→2024", f"{loss_area:.2f} ha", delta=-loss_area)
st.sidebar.metric("💚 GAIN 2020→2024", f"{gain_area:.2f} ha", delta=gain_area)

# MAP PANEL
col_map, col_chart = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ Peta Mangrove")

    m = geemap.Map(center=[-6.098, 106.765], zoom=15)

    if show_mvi:
        m.addLayer(
            mvi_dict[selected_year],
            {"min": -1, "max": 6, "palette": ["purple", "blue", "cyan", "green", "yellow", "red"]},
            f"MVI {selected_year}",
        )

    m.addLayer(
        mask_map_dict[selected_year],
        {"palette": ["#00FF00"]},
        f"Mangrove {selected_year}",
    )

    m.add_legend(title="Legend", legend_dict={"Mangrove": "#00FF00"})
    m.to_streamlit(height=600)

    st.subheader("📊 Tabel Luas Mangrove per Tahun")
    df_ts = pd.DataFrame(
        {
            "Tahun": years,
            "Luas (ha)": [area_dict[y] for y in years],
        }
    )
    st.table(df_ts)

# RIGHT PANEL – TIME SERIES & LOSS/GAIN
with col_chart:
    st.subheader("📈 Time Series Luas Mangrove")

    df_ts = pd.DataFrame(
        {
            "Tahun": years,
            "Luas (ha)": [area_dict[y] for y in years],
        }
    )

    fig_ts = px.line(df_ts, x="Tahun", y="Luas (ha)", markers=True)
    st.plotly_chart(fig_ts, use_container_width=True)

    st.subheader("🔥 Loss & Gain (2020→2024)")

    df_change = pd.DataFrame(
        {
            "Jenis": ["LOSS", "GAIN"],
            "Luas (ha)": [loss_area, gain_area],
        }
    )

    fig_lg = px.bar(
        df_change,
        x="Jenis",
        y="Luas (ha)",
        color="Jenis",
        text="Luas (ha)",
        color_discrete_map={"LOSS": "red", "GAIN": "green"},
    )
    st.plotly_chart(fig_lg, use_container_width=True)
