import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("A4F_API_KEY")
BASE_URL = "https://api.a4f.co/v1"

if not API_KEY:
    st.error("🔐 Please set your A4F_API_KEY in a `.env` file.")
    st.stop()

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

st.title("🛠️ A4F Prompt Enhancer")
raw = st.text_area("Enter your raw prompt:", height=200)
model = st.selectbox("Choose a model:", [
    "provider-2/gpt-3.5-turbo",
    "provider-5/gemini-2.5-flash-preview-04-17",
    "provider-1/gemini-2.0-flash"
])
stream = st.checkbox("Stream output live", value=False)

if st.button("Enhance"):
    if not raw.strip():
        st.warning("⚠️ Please provide a prompt to enhance.")
        st.stop()

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a prompt-enhancement assistant."},
                {"role": "user", "content": raw}
            ],
            temperature=0.7,
            max_tokens=400,
            stream=stream
        )

        if stream:
            st.subheader("🔄 Streaming Enhanced Prompt")
            text_buffer = ""
            for chunk in completion:
                delta = chunk.choices[0].delta.get("content", "")
                text_buffer += delta
                st.write(delta, end="")
            st.write("\n\n**Complete Enhancement:**")
            st.text(text_buffer)
        else:
            enhanced = completion.choices[0].message.content
            st.subheader("✅ Enhanced Prompt")
            st.write(enhanced)

    except Exception as e:
        st.error(f"❌ Enhancement failed – {e}")
