import streamlit as st
from groq import Groq
import datetime

# PAGE UI
st.title("🤖 UCUP AI Assistant")
st.markdown(
    """
    Tanyakan apa pun tentang **mangrove**, **turbiditas**, **banjir rob**, 
    **NDWI/NDTI**, **MVI**, atau kondisi lingkungan **Muara Angke (2020–2024)**.

    AI akan menjawab dengan penjelasan **jelas, sederhana, dan berbasis data**.
    """
)

st.divider()

# INIT GROQ CLIENT
def get_client():
    try:
        api_key = st.secrets["groq"]["api_key"]
        return Groq(api_key=api_key)
    except Exception:
        st.error("❌ Groq API key belum diatur di Secrets Streamlit.")
        st.stop()

client = get_client()

# TOMBOL RESET CHAT
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("♻️ Reset"):
        st.session_state.messages = []
        st.rerun()

# CHAT MEMORY
if "messages" not in st.session_state:
    st.session_state.messages = []

# TAMPILKAN CHAT SEBELUMNYA
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT BOX
placeholder_text = "Tanyakan sesuatu… "
user_input = st.chat_input(placeholder_text)

# KALO USER KIRIM PESAN
if user_input:

    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Proses AI
    with st.chat_message("assistant"):
        with st.spinner("AI sedang menganalisis data…"):

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=0.25,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Kamu adalah **UCUP AI Assistant**, asisten lingkungan Muara Angke. "
                            "Jawab dengan bahasa Indonesia atau bahasa menyesuaikan pengguna yang sangat jelas, sederhana, ramah, "
                            "UCUP merupakan kepanjangan dari Urban Rob Risk,Cover Mangrove, Under Water Pollution"
                            "dan terstruktur dalam poin-poin jika perlu.\n\n"
                            "Fokus menjelaskan:\n"
                            "- Mangrove & indeks MVI\n"
                            "- Kualitas air (NDWI, NDTI)\n"
                            "- Banjir rob (Flood Hazard Index)\n"
                            "- Interpretasi nilai citra satelit\n"
                            "- Data tahun 2020–2024\n\n"
                            "Kamu adalah asisten yang asik bisa diajak untuk berbicara konteks apapun terutama lingkungan "
                            "Bila pertanyaan tidak relevan, tetap tanggapi tapi arahkan kembali dengan sopan"
                        ),
                    },
                    *st.session_state.messages,
                ],
            )

            ai_answer = response.choices[0].message.content

            # Tampilkan jawaban
            st.markdown(ai_answer)

    # Simpan ke riwayat
    st.session_state.messages.append({"role": "assistant", "content": ai_answer})



