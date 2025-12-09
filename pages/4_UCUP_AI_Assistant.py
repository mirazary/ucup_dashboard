import streamlit as st
from groq import Groq

st.title("🤖 UCUP AI Assistant")
st.write(
    "Tanya apa pun tentang Mangrove, Turbiditas, Flood Hazard, Muara Angke, dll."
)

# ------------------------------------------------
# INIT GROQ CLIENT (API KEY DIAMBIL DARI SECRETS)
# ------------------------------------------------
def get_client():
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        st.error(
            "❌ GROQ_API_KEY belum diatur di Secrets.\n\n"
            "Masukkan API key Groq di Secrets terlebih dahulu."
        )
        st.stop()

    return Groq(api_key=api_key)

client = get_client()

# ------------------------------------------------
# SIMPAN RIWAYAT CHAT
# ------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# TAMPILKAN CHAT SEBELUMNYA
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# INPUT CHAT BARU
user_input = st.chat_input("Ketik pertanyaan kamu...")

if user_input:
    # Simpan & tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Panggil API Groq
    with st.chat_message("assistant"):
        with st.spinner("AI sedang mengetik..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Kamu adalah UCUP AI Assistant. "
                            "Fokus menjawab tentang mangrove, kualitas air, turbiditas, "
                            "banjir rob, dan lingkungan di Muara Angke. "
                            "Jawab dengan bahasa Indonesia yang jelas, sederhana, "
                            "dan terstruktur. Jika ada angka/indikator, jelaskan maknanya."
                        ),
                    },
                    *[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                ],
                temperature=0.3,
            )

            ai_answer = response.choices[0].message.content
            st.write(ai_answer)

    # Simpan jawaban AI ke riwayat
    st.session_state.messages.append(
        {"role": "assistant", "content": ai_answer}
    )
