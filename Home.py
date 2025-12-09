import streamlit as st

# PAGE CONFIG HANYA DI FILE INI
st.set_page_config(
    page_title="UCUP Dashboard",
    layout="wide",
    page_icon="🌀"
)

# HALAMAN UTAMA
st.title("🌀 UCUP Dashboard")
st.markdown(
    """
    ### **Urban Rob Risk • Cover Mangrove • Under Water Pollution**
    Selamat datang di **UCUP Dashboard** — sistem monitoring lingkungan untuk 
    kawasan **Muara Angke** yang menggabungkan analisis *mangrove*, 
    *turbiditas*, dan *flood hazard*.

    Gunakan sidebar untuk berpindah halaman:
    - 🌊 Urban Rob Risk (Flood Hazard Index)
    - 🌿 Cover Mangrove
    - 💧 Under Water Pollution
    - 🤖 UCUP AI Assistant
    """
)

st.divider()

# CARD STYLE
card_style = """
    background-color:{bg};
    padding:20px;
    border-radius:15px;
    height:200px;
    color:#1a1a1a;
    font-weight:430;
"""

# CARD LAYOUT
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="{card_style.format(bg='#e8f4f8')}">
        <h3 style="color:#0f2a44;">🌊 Urban Rob Risk</h3>
        <p style="font-size:14px;">
            Analisis banjir rob berbasis GIS:
            distance-to-water, DEM SRTM,
            TPI, NDWI, dan NDVI.
        </p>
        <b>Output:</b> Flood Hazard Index (1–5)
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="{card_style.format(bg='#e9f7ef')}">
        <h3 style="color:#184d28;">🌿 Cover Mangrove</h3>
        <p style="font-size:14px;">
            Pemantauan luas mangrove (2020–2024)
            menggunakan MVI dari Sentinel-2.
        </p>
        <b>Output:</b> Luas, gain/loss, time series
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="{card_style.format(bg='#fef6e4')}">
        <h3 style="color:#7a4c05;">💧 Under Water Pollution</h3>
        <p style="font-size:14px;">
            Analisis kualitas air melalui NDWI
            dan NDTI untuk melihat turbiditas.
        </p>
        <b>Output:</b> Statistik, histogram, peta
    </div>
    """, unsafe_allow_html=True)

st.divider()

# AI UCUP ASSISTANT 
st.markdown(
    """
    ### 🤖 **UCUP AI Assistant**
    Tanyakan apa pun tentang mangrove, turbiditas, banjir rob, atau lingkungan Muara Angke.
    AI akan menjawab dengan penjelasan yang mudah dipahami.
    """
)
st.info("Pergi ke halaman **UCUP AI Assistant** dari sidebar (folder `pages`).", icon="💬")

# Footer
st.markdown(
    """
    <br>
    <center style='opacity: 0.5; font-size:13px;'>
    © 2025 UCUP Dashboard — Built with Streamlit & Google Earth Engine
    </center>
    """,
    unsafe_allow_html=True
)
