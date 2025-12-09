import streamlit as st

# PAGE CONFIG (hanya file ini yang punya)
st.set_page_config(
    page_title="UCUP",
    layout="wide",
    page_icon="🌀",
)

# HERO SECTION
st.markdown(
    """
    <div style="padding: 30px 20px; text-align: center;">
        <h1 style="font-size: 48px; margin-bottom: -10px;">🌀 UCUP</h1>
        <p style="font-size: 20px; color: #666;">
            <b>Urban Rob Risk • Cover Mangrove • Under Water Pollution</b>
        </p>
        <p style="font-size: 16px; color: #888; margin-top: -10px;">
            Analisis lingkungan kawasan Muara Angke menggunakan citra satelit
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# CARD STYLE
card_style = """
    background-color:{bg};
    padding: 22px;
    border-radius: 18px;
    height: 220px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: 0.3s;
"""

hover_script = """
    <script>
    const cards = window.document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseover', () => {
            card.style.transform = 'scale(1.02)';
            card.style.boxShadow = '0 6px 16px rgba(0,0,0,0.12)';
        });
        card.addEventListener('mouseout', () => {
            card.style.transform = 'scale(1)';
            card.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
        });
    });
    </script>
"""

# 3 FEATURE CARDS
card_style = """
    background-color:{bg};
    padding: 22px;
    border-radius: 18px;
    height: 220px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: 0.3s;
    color: #111111; /* teks jauh lebih gelap */
"""

title_style = "font-size: 20px; font-weight: 700; margin-bottom: 6px;"
body_style  = "font-size: 15px; line-height: 1.45; color: #222222;"  # kontras tinggi
bold_style  = "font-weight: 600; color: #000000;"                    # super tajam

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card" style="{card_style.format(bg='#e8f4f8')}">
        <div style="{title_style} color:#0f2a44;">🌊 Urban Rob Risk</div>
        <p style="{body_style}">
            Analisis potensi banjir rob berbasis GIS:<br>
            • Distance-to-water<br>
            • DEM SRTM<br>
            • TPI, NDWI, NDVI
        </p>
        <span style="{bold_style}">Output:</span> Flood Hazard Index
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="{card_style.format(bg='#e9f7ef')}">
        <div style="{title_style} color:#184d28;">🌿 Cover Mangrove</div>
        <p style="{body_style}">
            Pemantauan tutupan mangrove tahunan (2020–2024)
            menggunakan indeks MVI dari Sentinel-2.
        </p>
        <span style="{bold_style}">Output:</span> Luas area, tren, gain/loss
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card" style="{card_style.format(bg='#fef6e4')}">
        <div style="{title_style} color:#7a4c05;">💧 Under Water Pollution</div>
        <p style="{body_style}">
            Analisis kualitas air & kekeruhan:<br>
            • NDWI <br>
            • NDTI 
        </p>
        <span style="{bold_style}">Output:</span> Peta & Histogram NDTI
    </div>
    """, unsafe_allow_html=True)

# AI UCUP ASSISTANT
st.markdown(
    """
    <div style="padding-top:20px;">
        <h2>🤖 UCUP AI Assistant</h2>
        <p style="font-size:16px; color:#666; max-width:700px;">
            Tanyakan apa pun tentang mangrove, turbiditas, banjir rob, atau 
            kondisi lingkungan Muara Angke (2020–2024).
            Sistem AI akan menjawab dengan bahasa yang mudah dipahami.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info("Pergi ke halaman **UCUP AI Assistant** dari sidebar di kiri.", icon="💬")

# FOOTER
st.markdown(
    """
    <br><br>
    <center style='opacity: 0.55; font-size:13px;'>
        © 2025 UCUP Dashboard — Built with Streamlit & Google Earth Engine<br>
        Data menggunakan rentang tahun <b>2020 hingga 2024</b>
    </center>
    """,
    unsafe_allow_html=True
)




