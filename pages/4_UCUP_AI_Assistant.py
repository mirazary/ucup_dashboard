import streamlit as st
from groq import Groq

st.title("🤖 UCUP AI Assistant")
st.write("Tanya apa pun tentang Mangrove, Turbiditas, Flood Hazard, Muara Angke, dll.")

# Init Groq client
client = Groq(api_key='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')

# Simpan riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan semua chat sebelumnya
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input chat baru (seperti WhatsApp)
user_input = st.chat_input("Ketik pertanyaan kamu...")

if user_input:
    # Tampilkan chat user
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Proses AI
    with st.chat_message("assistant"):
        with st.spinner("AI sedang mengetik..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Kamu asisten UCUP Dashboard. Jawab jelas & sederhana."},
                    *[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                ],
                temperature=0.3
            )

            ai_answer = response.choices[0].message.content
            st.write(ai_answer)

    # Simpan jawaban AI
    st.session_state.messages.append({"role": "assistant", "content": ai_answer})
