import os, time, requests, streamlit as st
from dotenv import load_dotenv

# ─── Load Key ───────────────────────────────────
load_dotenv()
API_KEY = os.getenv("A4F_API_KEY")
if not API_KEY:
    st.error("🔒 Missing A4F_API_KEY in your environment.")
    st.stop()

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# ─── UI ─────────────────────────────────────────
st.title("A4F Image Generator (Fixed Models)")

# Use your known models
MODELS = [
    "provider-4/imagen-3",
    "provider-4/imagen-4",
    "provider-1/FLUX.1-schnell",
    "provider-6/sana-1.5-flash"
]

model   = st.selectbox("Choose image model", MODELS)
prompt  = st.text_input("Enter image prompt")
size    = st.selectbox("Size", ["256x256", "512x512", "1024x1024"])
quality = st.selectbox("Quality", ["standard", "hd"])
fmt     = st.selectbox("Response format", ["url", "b64_json"])

# ─── Helper: Generate with Retries ─────────────
def generate_image(payload, max_retries=3):
    url   = "https://api.a4f.co/v1/images/generations"
    delay = 1
    for _ in range(max_retries):
        r = requests.post(url, json=payload, headers=HEADERS)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 500:
            time.sleep(delay); delay *= 2; continue
        r.raise_for_status()
    return None

# ─── On Click ──────────────────────────────────
if st.button("Generate Image"):
    if not prompt.strip():
        st.error("❗ Prompt cannot be empty.")
    else:
        payload = {
            "model":            model,
            "prompt":           prompt,
            "n":                1,
            "size":             size,
            "quality":          quality,
            "response_format":  fmt,
        }
        with st.spinner("Generating…"):
            result = generate_image(payload)
            if not result:
                st.error("⚠️ Server error after retries. Try smaller size or simpler prompt.")
            else:
                data = result["data"][0]
                if fmt == "url":
                    img_url = data["url"]
                    st.image(img_url, caption=f"{model} ({size}, {quality})", use_column_width=True)
                    img_bytes = requests.get(img_url).content
                    st.download_button("Download PNG", img_bytes, "generated.png", "image/png")
                else:
                    st.image(data["b64_json"], caption=f"{model} (base64)", use_column_width=True)