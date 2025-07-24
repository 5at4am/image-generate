import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

# --- Load API Key ---
load_dotenv()
API_KEY = os.getenv("A4F_API_KEY")
if not API_KEY:
    st.error("🔒 Missing A4F_API_KEY in your environment.")
    st.stop()

# --- Universal Headers ---
# Use a base header for JSON requests
JSON_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
# Use a separate header for multipart requests (file uploads)
MULTIPART_HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# --- Generic Error Handling Request Function ---
def make_request(method, url, headers, **kwargs):
    """A robust function to handle API requests and errors."""
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        # Handle different content types in response
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        return response.content
    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP Error: {err}")
        # Try to show detailed error from server response text
        st.error(f"Server Response: {err.response.text}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Helper: Prompt Enhancer ---
def enhance_prompt(user_prompt):
    url = "https://api.a4f.co/v1/chat/completions"
    payload = {
        "model": "provider-2/gpt-3.5-turbo",
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
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.85,
    }
    response = make_request("post", url, headers=JSON_HEADERS, json=payload)
    return response["choices"][0]["message"]["content"] if response else None

# --- CHAT HELPER FUNCTION ---
def get_chat_completion(messages, model):
    """Handles the API call for the chat completion feature."""
    url = "https://api.a4f.co/v1/chat/completions"
    payload = {"model": model, "messages": messages}
    response = make_request("post", url, headers=JSON_HEADERS, json=payload)
    
    # Check for a valid response before trying to access its content
    if response and "choices" in response and response["choices"]:
        return response["choices"][0]["message"]["content"]
    else:
        # Return a friendly error message if the response is invalid or empty
        return "Sorry, I couldn't get a response. Please check the error messages above."

# --- Helper: Image Generator with Retry ---
def generate_image(payload, max_retries=3):
    url = "https://api.a4f.co/v1/images/generations"
    for i in range(max_retries):
        response = make_request("post", url, headers=JSON_HEADERS, json=payload)
        if response:
            return response
        st.warning(f"Attempt {i+1} failed. Retrying...")
        time.sleep(2**i) # Exponential backoff
    st.error("Failed to generate image after several retries.")
    return None

# --- Helper: Image Editor ---
def edit_image(payload, image_file, mask_file=None):
    url = "https://api.a4f.co/v1/images/edits"
    files = {"image": image_file}
    if mask_file:
        files["mask"] = mask_file
    return make_request("post", url, headers=MULTIPART_HEADERS, data=payload, files=files)

# --- Helper: Embeddings Generator ---
def create_embeddings(payload):
    url = "https://api.a4f.co/v1/embeddings"
    return make_request("post", url, headers=JSON_HEADERS, json=payload)

# --- Helper: Text-to-Speech ---
def text_to_speech(payload):
    url = "https://api.a4f.co/v1/audio/speech"
    return make_request("post", url, headers=JSON_HEADERS, json=payload)

# --- Helper: Speech-to-Text ---
def speech_to_text(payload, audio_file):
    url = "https://api.a4f.co/v1/audio/transcriptions"
    files = {"file": audio_file}
    return make_request("post", url, headers=MULTIPART_HEADERS, data=payload, files=files)

# --- Helper: Video Generator ---
def generate_video(payload):
    url = "https://api.a4f.co/v1/video/generations"
    return make_request("post", url, headers=JSON_HEADERS, json=payload)

# --- Helper: List Models ---
def list_models():
    url = "https://api.a4f.co/v1/models"
    return make_request("get", url, headers=JSON_HEADERS)

# --- Helper: Get Usage ---
def get_usage(start_date, end_date):
    url = f"https://api.a4f.co/v1/usage?start_date={start_date}&end_date={end_date}"
    return make_request("get", url, headers=JSON_HEADERS)


# --- UI: Title & Tabs ---
st.title("A4F API Suite")
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "💬 Chat", "🖼️ Image Generation", "🎨 Image Edits", "🔡 Embeddings", "🗣️ Text-to-Speech",
    "🎤 Speech-to-Text", "🎬 Video Generation", "📦 List Models", "📊 Get Usage"
])
# --- UI: Chat Tab ---
with tab0:
    st.header("💬 Chat Completion")
    chat_model = st.selectbox("Choose a chat model", [
        "provider-2/gpt-3.5-turbo",
        "provider-1/gemma-3-12b-it",
        "provider-1/gemma-2-27b-it",
        "provider-1/gemini-2.0-flash-lite-001",
        "provider-2/gemini-2.0-flash",
        "provider-6/gemini-2.5-flash",
        "provider-6/gemini-2.5-flash-thinking",
        "provider-3/gpt-4o-mini",
        "provider-3/gpt-4",
        "provider-6/gpt-4.1-mini",
        "provider-6/gpt-4.1-nano",
        "provider-6/gpt-4o-mini-search-preview",
        "provider-6/gpt-4o",
        "provider-6/o3-high",
        "provider-6/gpt-4.1",
        "provider-1/llama-3.3-70b-instruct-turbo",
        "provider-2/codestral",
        "provider-1/llama-4-maverick-17b-128e",
        "provider-2/llama-4-maverick",
        "provider-2/llama-4-scout",
        "provider-3/llama-3.2-3b",
        "provider-3/llama-3.3-70b",
        "provider-2/qwq-32b",
        "provider-3/qwen-3-235b-a22b-2507",
        "provider-3/deepseek-v3",
        "provider-3/deepseek-v3-0324",
        "provider-6/kimi-k2",
        "provider-3/qwen-3-235b-a22b",
        "provider-6/minimax-m1-40k"

    ], key="chat_model")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_chat_completion(st.session_state.messages, chat_model)
                st.markdown(response)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- UI: Image Generation Tab ---
with tab1:
    st.header("🖼️ Image Generation")
    MODELS = [
        "provider-4/imagen-3", "provider-4/imagen-4", "provider-1/FLUX.1-schnell",
        "provider-2/FLUX.1-schnell", "provider-3/imagen-3.0-generate-002",
        "provider-3/imagen-4.0-generate-preview-06-06", "provider-6/sana-1.5-flash",
        "provider-2/dall-e-3", "provider-6/sana-1.5", "provider-3/FLUX.1-dev",
        "provider-6/FLUX.1.1-pro", "provider-1/FLUX.1.1-pro", "provider-6/FLUX.1-kontext-dev",
        "provider-1/FLUX.1-kontext-pro", "provider-6/FLUX.1-kontext-max",
        "provider-2/FLUX.1-schnell-v2"
    ]
    model = st.selectbox("Choose image model", MODELS, key="ig_model")
    prompt = st.text_input("Enter image prompt", key="ig_prompt")
    size = st.selectbox("Size", ["256x256", "512x512", "1024x1024"], key="ig_size")
    quality = st.selectbox("Quality", ["standard", "hd"], key="ig_quality")
    fmt = st.selectbox("Response format", ["url", "b64_json"], key="ig_fmt")
    n = st.slider("How many images to generate?", 1, 12, 4, key="ig_n")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧠 Enhance Prompt"):
            if not prompt.strip():
                st.warning("⚠️ Please enter a prompt first.")
            else:
                with st.spinner("Enhancing prompt..."):
                    enhanced = enhance_prompt(prompt)
                    if enhanced:
                        st.success("✅ Enhanced prompt generated below:")
                        st.text_area("Enhanced Prompt", enhanced, height=100, key="ig_enhanced")

    with col2:
        if st.button("🎨 Generate Image"):
            if not prompt.strip():
                st.error("❗ Prompt cannot be empty.")
            else:
                payload = {
                    "model": model, "prompt": prompt, "n": n,
                    "size": size, "quality": quality, "response_format": fmt,
                }
                with st.spinner("Generating images..."):
                    result = generate_image(payload)
                    if result and "data" in result:
                        cols = st.columns(min(n, len(result["data"])))
                        for idx, data in enumerate(result["data"]):
                            with cols[idx % len(cols)]:
                                if fmt == "url":
                                    img_url = data["url"]
                                    st.image(img_url, caption=f"Image {idx+1}", use_container_width=True)
                                    try:
                                        img_bytes = requests.get(img_url).content
                                        st.download_button("Download PNG", img_bytes, f"image_{idx+1}.png", "image/png", key=f"dl_{idx}")
                                    except Exception as e:
                                        st.error(f"Could not download image {idx+1}")
                                else:
                                    st.image(data["b64_json"], caption=f"Image {idx+1}", use_container_width=True)

# --- UI: Image Edits Tab ---
with tab2:
    st.header("🎨 Image Edits")
    edit_model = st.selectbox("Choose edit model", ["provider-6/black-forest-labs-flux-1-kontext-dev","provider-6/black-forest-labs-flux-1-kontext-pro","provider-6/black-forest-labs-flux-1-kontext-max"], key="ie_model")
    edit_prompt = st.text_area("What to change in the image?", key="ie_prompt")
    image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="ie_image")
    mask_file = st.file_uploader("Upload a mask (optional)", type=["png"], key="ie_mask")
    edit_size = st.selectbox("Size", ["256x256", "512x512", "1024x1024"], key="ie_size")
    edit_n = st.slider("Number of edited images", 1, 4, 1, key="ie_n")

    if st.button("🖌️ Edit Image"):
        if not all([edit_prompt, image_file]):
            st.warning("Please provide a prompt and an image.")
        else:
            payload = {
                "prompt": edit_prompt,
                "model": edit_model,
                "n": str(edit_n),
                "size": edit_size
            }
            with st.spinner("Editing image..."):
                result = edit_image(payload, image_file, mask_file)
                if result and "data" in result:
                    st.success("Edit complete!")
                    cols = st.columns(min(edit_n, len(result["data"])))
                    for i, img_data in enumerate(result["data"]):
                        with cols[i]:
                            st.image(img_data["url"], caption=f"Edited Image {i+1}", use_container_width=True)

# --- UI: Embeddings Tab ---
with tab3:
    st.header("🔡 Embeddings")
    embed_model = st.selectbox("Choose embedding model", ["provider-2/text-embedding-3-small","provider-3/text-embedding-ada-002"], key="em_model")
    embed_input = st.text_area("Text to embed", key="em_input")

    if st.button("Generate Embeddings"):
        if embed_input.strip():
            payload = {"model": embed_model, "input": embed_input}
            with st.spinner("Generating embeddings..."):
                result = create_embeddings(payload)
                if result:
                    st.success("Embeddings generated!")
                    st.json(result)
        else:
            st.warning("Please enter text to embed.")

# --- UI: Text-to-Speech Tab ---
with tab4:
    st.header("🗣️ Text-to-Speech")
    tts_model = st.selectbox("Choose TTS model", ["provider-3/tts-1", "provider-2/tts-1-hd", "provider-6/sonic-2", "provider-6/sonic"], key="tts_model")
    tts_input = st.text_area("Text to convert to speech", key="tts_input")
    tts_voice = st.selectbox("Choose a voice (for tts-1 models)", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"], key="tts_voice")
    
    if st.button("🔊 Generate Speech"):
        if tts_input.strip():
            payload = {"model": tts_model, "input": tts_input}
            if "tts-1" in tts_model:
                 payload["voice"] = tts_voice
            with st.spinner("Generating audio..."):
                audio_content = text_to_speech(payload)
                if audio_content:
                    st.audio(audio_content, format="audio/mp3")
        else:
            st.warning("Please enter text for speech synthesis.")

# --- UI: Speech-to-Text Tab ---
with tab5:
    st.header("🎤 Speech-to-Text")
    stt_model = st.selectbox("Choose STT model", ["provider-2/whisper-1", "provider-6/distil-whisper-large-v3-en", "provider-3/gpt-4o-mini-transcribe"], key="stt_model")
    audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"], key="stt_file")

    if st.button("Transcribe Audio"):
        if audio_file:
            payload = {"model": stt_model}
            with st.spinner("Transcribing audio..."):
                result = speech_to_text(payload, audio_file)
                if result and "text" in result:
                    st.success("Transcription complete!")
                    st.text_area("Transcription", result["text"], height=150)
        else:
            st.warning("Please upload an audio file.")

# --- UI: Video Generation Tab ---
with tab6:
    st.header("🎬 Video Generation")
    video_model = st.selectbox("Choose video model", ["provider-6/wan-2.1"], key="vg_model")
    video_prompt = st.text_area("Video prompt", key="vg_prompt")
    aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "1:1", "9:16"], key="vg_aspect")

    if st.button("Generate Video"):
        if not video_prompt.strip():
            st.warning("Please enter a video prompt.")
        else:
            payload = {"model": video_model, "prompt": video_prompt, "aspect_ratio": aspect_ratio}
            with st.spinner("Generating video... This may take a moment."):
                result = generate_video(payload)
                if result and "data" in result:
                    st.success("Video Generated!")
                    video_url = result["data"][0]["url"]
                    st.video(video_url)

# --- UI: List Models Tab ---
with tab7:
    st.header("📦 List Models")
    if st.button("Fetch Available Models"):
        with st.spinner("Fetching models..."):
            models = list_models()
            if models:
                st.success(f"Found {len(models.get('data', []))} models.")
                st.json(models)

# --- UI: Get Usage Tab ---
with tab8:
    st.header("📊 Get Usage")
    from datetime import date, timedelta
    today = date.today()
    start_date = st.date_input("Start date", today - timedelta(days=30))
    end_date = st.date_input("End date", today)

    if st.button("Fetch Usage Data"):
        with st.spinner("Fetching usage data..."):
            # Format dates as YYYY-MM-DD strings
            usage_data = get_usage(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            if usage_data:
                st.json(usage_data)