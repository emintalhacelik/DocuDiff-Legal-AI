<div align="center">

# ⚖️ DocuDiff Legal AI
### Intelligent Commercial Contract Risk Assessment & Executive Redlining

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://www.python.org/downloads/)
[![AI Engine: Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%20Flash-indigo.svg)](https://ai.google.dev/)
[![Framework: Flask](https://img.shields.io/badge/Backend-Flask-black.svg)](https://flask.palletsprojects.com/)
[![Styling: Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38bdf8.svg)](https://tailwindcss.com/)

**DocuDiff Legal AI** is an open-source, corporate-grade contract intelligence platform designed to review commercial contracts, detect hidden legal risks, translate dense legalese into plain executive English, and propose balanced, commercially reasonable redline revisions.

[Features](#-key-features) • [Quickstart](#-quickstart-guide) • [Docker](#-docker-deployment) • [Architecture](#-project-structure) • [Author](#-author--contact)

---

</div>

## 🚀 Key Features

* **🤖 Multi-Model AI Risk Intelligence:** Leverages Google Gemini with resilient automatic fallback chains to prevent service disruptions.
* **📄 PDF Contract Parsing:** Upload full PDF agreements via drag-and-drop; text is extracted instantly using `pdfplumber`.
* **⚖️ Custom Reviewer Perspectives:**
  * **Balanced Corporate Counsel** — standard, commercially reasonable terms.
  * **Buyer / Client Protection** — aggressive defense against vendor lock-in, uncapped liabilities, and unilateral fee hikes.
  * **Vendor / Supplier Protection** — safeguards intellectual property, payment timeliness, and liability caps.
* **🌓 Dark & High-Contrast Light Mode:** Built-in theme switcher with high-contrast typography in both modes.
* **🌐 Internationalization (i18n):** 100% English by default, with one-click live toggle to **Türkçe**.
* **🔐 Full Authentication & SQLite Persistence:** User registration, password hashing (`Flask-Bcrypt`), session management (`Flask-Login`), and a searchable personal review history sidebar.
* **📋 1-Click Clipboard Utilities:** Auto-copy redline revisions, copy email, and export analysis data.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.10, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt
* **AI Integration:** Google GenAI SDK (`google-genai`), Gemini 3.5 Flash / Gemini 3.8 Flash
* **PDF Engine:** `pdfplumber`
* **Database:** SQLite (`models.py`)
* **Frontend:** Tailwind CSS, JetBrains Mono & Playfair Display typography, Vanilla JavaScript (zero heavy SPA runtime required)

---

## ⚡ Quickstart Guide

### Do Not Download App, Access With Web Service
```bash
You can click this link to access fast (https://docudiff-legal-ai.onrender.com/)
```

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/DocuDiff-Legal-AI.git
cd DocuDiff-Legal-AI
```


### 2. Create and Activate Virtual Environment
```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and supply your [Google Gemini API Key](https://aistudio.google.com/app/apikey):
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
SECRET_KEY=generate_a_random_secret_for_sessions
```

### 5. Launch the Application
```bash
python app.py
```
Visit **`http://127.0.0.1:5000`** in your browser.



---

## 🐳 Docker Deployment

Run DocuDiff Legal AI anywhere with zero local Python setup:

```bash
docker compose up -d
```
The application will be accessible at `http://localhost:5000`.

---

## 📁 Project Structure

```text
DocuDiff-Legal-AI/
├── app.py                # Main Flask application & routing (Auth, PDF, Analyze, History)
├── legal_ai.py           # Gemini AI core engine, system prompt, and fallback chain
├── models.py             # SQLAlchemy User and Analysis database models
├── config.py             # Configuration and environment loader
├── requirements.txt      # Project Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Docker Compose multi-service definition
├── Procfile              # PaaS production process file (Render, Railway, Heroku)
├── LICENSE               # MIT Open Source License
├── .env.example          # Sample environment configuration template
├── static/               # Uploads and static media assets
└── templates/            # Frontend HTML templates
    ├── index.html        # Main contract analysis dashboard & history sidebar
    ├── login.html        # User sign-in screen
    └── register.html     # User registration screen
```

---

## 🔒 Security & Privacy

* **Local Storage:** Contract text and analysis history are stored in your own SQLite database (`instance/docudiff.db`).
* **Secrets Protection:** Secret keys and `.env` files are ignored by default in `.gitignore` to prevent leaking credentials.
* **Passwords:** Passwords are salted and hashed using bcrypt before persistence.

---

## ⚖️ Legal Disclaimer

DocuDiff Legal AI is developed for informational risk screening and drafting assistance. It does not constitute formal legal counsel or create an attorney-client relationship. Always consult a licensed attorney for binding commercial transactions.

---

## 👨‍💻 Author & Contact

**Emin Talha Çelik**
* **LinkedIn:** [linkedin.com/in/emintalhacelik](https://www.linkedin.com/in/emintalhacelik)
* **Email:** [emintalhacelik@gmail.com](mailto:emintalhacelik@gmail.com)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — free to use, modify, and distribute for personal and commercial purposes.
