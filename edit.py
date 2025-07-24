import os
import streamlit as st
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("A4F_API_KEY")
BASE_URL = "https://api.a4f.co/v1/images/edits"

if not API_KEY:
    st.error("🔐 Please set your A4F_API_KEY in a `.env` file.")
    st.stop()

st.title("🖼️ A4F Image Editor — WAN 2.1")
img = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
mask = st.file_uploader("Upload a mask (optional)", type=["png", "jpg", "jpeg"])
prompt = st.text_area("Describe the edit you want:", height=100)
size = st.selectbox("Choose size", ["256x256", "512x512", "1024x1024"])

if st.button("✨ Edit Image"):
    if not img or not prompt.strip():
        st.warning("⚠️ Please upload an image and provide a prompt.")
        st.stop()

    # Prepare payload
    files = {
        "image": ("image.png", img, img.type),
        "prompt": (None, prompt),
        "size": (None, size),
        "model": (None, "provider-6/wan-2.1")
    }
    if mask:
        files["mask"] = ("mask.png", mask, mask.type)

    headers = {"Authorization": f"Bearer {API_KEY}"}

    # Send request
    resp = requests.post(BASE_URL, headers=headers, files=files)

    if resp.status_code == 200:
        data = resp.json()
        if data.get("data"):
            img_url = data["data"][0]["url"]
            st.success("✅ Image edited successfully!")
            st.image(img_url, use_column_width=True)
        else:
            st.error("❌ Unexpected response structure.")
    else:
        st.error(f"❌ API Error {resp.status_code}: {resp.text}")

    # Download button
    if data.get("data"):
        img_url = data["data"][0]["url"]
        img_bytes = requests.get(img_url).content
        st.download_button("Download PNG", img_bytes, "edited.png", "image/png")
        st.stop()
        1