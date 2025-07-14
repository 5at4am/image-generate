🎨 A4F Image Generator + Prompt Enhancer

A powerful web-based tool that enhances your image generation prompts using AI and generates stunning visuals via A4F’s API. Built with [Streamlit](https://streamlit.io/) and powered by `uv` for efficient dependency management.

---

## 🚀 Features

- 🔐 Secure API key management via `.env`
- 🧠 AI-based prompt enhancement using Gemini model (`provider-5/gemini-2.5-flash-preview-04-17`)
- 🖼️ Image generation using multiple models (FLUX, Imagen, Sana, etc.)
- 🎛️ Selectable image size, quality, format, and number of outputs
- 🌙 Dark mode toggle for improved UI experience
- 📜 Image generation history with preview & download support
- 🐞 Debug mode for developers

---

## 🧰 Tech Stack

| Tool          | Purpose                                  |
|---------------|------------------------------------------|
| `Streamlit`   | Frontend UI & interaction logic          |
| `uv`          | Fast Python dependency manager & runner  |
| `A4F API`     | AI-powered prompt enhancement & images   |
| `dotenv`      | Secure environment variable handling     |
| `requests`    | API communication                        |

---

## 📦 Installation & Setup

Make sure you have [`uv`](https://github.com/astral-sh/uv) installed. If not:

```bash
pip install uv
# Step 1: Initialize the environment
uv init

# Step 2: Install dependencies
uv install streamlit openai requests python-dotenv

# Step 3: Add your API key
# Create a .env file in the root directory and add:
A4F_API_KEY=your_api_key_here

# Step 4: Run the app
uv run streamlit run main.py