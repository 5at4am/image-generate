import os, time, requests, streamlit as st
from dotenv import load_dotenv

# ─── Load API Key ───────────────────────────────
load_dotenv()
API_KEY = os.getenv("A4F_API_KEY")
if not API_KEY:
    st.error("🔒 Missing A4F_API_KEY in your environment.")
    st.stop()

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# ─── Session State Init ────────────────────────
if "history" not in st.session_state:
    st.session_state["history"] = []

if "enhanced" not in st.session_state:
    st.session_state["enhanced"] = ""

# ─── Helper: Prompt Enhancer ────────────────────
def enhance_prompt(user_prompt):
    url = "https://api.a4f.co/v1/chat/completions"
    payload = {
        "model": "provider-5/gemini-2.5-flash-preview-04-17",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert AI prompt engineer specialized in generative image models like Imagen, FLUX, and DALL·E. "
                    "Given a raw or vague prompt, you will transform it into a highly detailed and creative visual description that helps the model produce stunning results.\n\n"
                    "Your enhanced prompt should:\n"
                    "• Include clear **visual elements**, **lighting**, **composition**, and **style**\n"
                    "• Use vivid descriptive language and modifiers\n"
                    "• Mention camera angles, medium (e.g., oil painting, 3D render), environment, mood, or time of day if possible\n"
                    "• Avoid repeating the original input; expand on it professionally\n\n"
                    "Format: Return only the improved image prompt, no extra text."
                )
            },
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.85,
        "stream": False
    }
    try:
        r = requests.post(url, headers=HEADERS, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        if debug:
            st.exception(e)
        else:
            st.error(f"Enhancement failed: {e}")
        return None

# ─── Helper: Image Generator ────────────────────
def generate_image(payload, max_retries=3):
    url = "https://api.a4f.co/v1/images/generations"
    delay = 1
    for _ in range(max_retries):
        r = requests.post(url, json=payload, headers=HEADERS)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 500:
            time.sleep(delay); delay *= 2; continue
        if debug:
            st.warning(f"Debug Error Response:\n{r.text}")
        r.raise_for_status()
    return None

# ─── UI: Settings ───────────────────────────────
st.set_page_config(layout="wide")
st.title("🎨 A4F Image Generator + Prompt Enhancer")

# ─── Debug and Theme Toggles ────────────────────
debug = st.sidebar.checkbox("🐞 Debug Mode")
dark = st.sidebar.checkbox("🌙 Dark Theme")
if dark:
    st.markdown(
        """
        <style>
        body, .stApp { background-color: #1e1e1e; color: white; }
        </style>
        """, unsafe_allow_html=True
    )

# ─── Prompt Input & Presets ─────────────────────
preset = st.selectbox("🎯 Choose a prompt preset", [
    "", 
    "Futuristic neon city skyline at night, wide shot, highly detailed",
    "Fantasy forest with glowing mushrooms and fog, cinematic, top-down",
    "Oil painting of a serene ocean during sunset, golden lighting",
    "Low-poly voxel winter village scene, isometric view, stylized"
])

prompt = st.text_input("📝 Enter your image prompt", value=preset or "")

# ─── Enhance Prompt UI ──────────────────────────
if st.button("🧠 Enhance Prompt"):
    if not prompt.strip():
        st.warning("⚠️ Please enter a prompt first.")
    else:
        with st.spinner("Enhancing..."):
            enhanced = enhance_prompt(prompt)
            if enhanced:
                st.session_state["enhanced"] = enhanced
                st.success("✅ Enhanced Prompt:")
                st.text_area("Enhanced Prompt", enhanced, height=100)

# ─── Use Enhanced Prompt Button ─────────────────
if st.session_state["enhanced"]:
    if st.button("📥 Use Enhanced Prompt for Generation"):
        prompt = st.session_state["enhanced"]

# ─── Model + Settings ───────────────────────────
MODELS = [
    "provider-4/imagen-3",
    "provider-4/imagen-4",
    "provider-1/FLUX.1-schnell",
    "provider-6/sana-1.5-flash"
]

model   = st.selectbox("📌 Choose image model", MODELS)
size    = st.selectbox("📐 Image size", ["256x256", "512x512", "1024x1024"])
quality = st.selectbox("🌟 Quality", ["standard", "hd"])
fmt     = st.selectbox("🧾 Response format", ["url", "b64_json"])
n       = st.slider("🖼️ Number of images", 1, 12, 4)

# ─── Generate Image ─────────────────────────────
if st.button("🎨 Generate Images"):
    if not prompt.strip():
        st.error("❗ Prompt cannot be empty.")
    else:
        payload = {
            "model":            model,
            "prompt":           prompt,
            "n":                n,
            "size":             size,
            "quality":          quality,
            "response_format":  fmt,
        }

        with st.spinner("Generating images..."):
            result = generate_image(payload)
            if not result:
                st.error("⚠️ Server error. Try again.")
            else:
                st.session_state["history"].append(result)
                cols = st.columns(3)
                for idx, data in enumerate(result["data"]):
                    with cols[idx % 3]:
                        if fmt == "url":
                            img_url = data["url"]
                            st.image(img_url, caption=f"Image {idx+1}", use_container_width=True)
                            img_bytes = requests.get(img_url).content
                            st.download_button("⬇️ Download", img_bytes, f"image_{idx+1}.png", "image/png")
                        else:
                            st.image(data["b64_json"], caption=f"Image {idx+1}", use_container_width=True)

# ─── Image History View ─────────────────────────
if st.checkbox("🕘 Show Image History"):
    for run in st.session_state["history"]:
        st.subheader("🖼️ Previous Generation")
        cols = st.columns(3)
        for idx, data in enumerate(run["data"]):
            with cols[idx % 3]:
                if fmt == "url":
                    st.image(data["url"], caption=f"History Image {idx+1}", use_container_width=True)
                else:
                    st.image(data["b64_json"], caption=f"History Image {idx+1}", use_container_width=True)
