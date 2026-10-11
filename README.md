# 🤖 Ollama LangChain RAG Assistant

A full-stack, privacy-focused AI assistant powered by **Ollama**, **LangChain**, and **FAISS Vector Database**. Features an advanced **Retrieval-Augmented Generation (RAG)** pipeline for PDF question answering, an autonomous multi-tool routing agent, JWT-based user authentication, and a dedicated **Admin Management Portal**.

---

## ✨ Features

- **🔒 Local & Private AI Execution**: Powered by local Ollama models (`llama3.2`, `mistral`, `gemma2`, `codellama`) with complete data privacy and zero API costs.
- **📄 Advanced PDF RAG Pipeline**:
  - Upload PDF documents via a pin icon (`📎`) for instantaneous indexing.
  - Semantic chunking via LangChain `RecursiveCharacterTextSplitter`.
  - Dense vector embeddings using HuggingFace `all-MiniLM-L6-v2`.
  - Fast similarity search powered by **FAISS CPU**.
  - Multi-method fallback document loaders (`PyPDFLoader` ➔ `pypdf` ➔ `PyPDF2`) with empty/scanned document validation.
  - **Strict PDF Mode**: Restricts LLM responses strictly to document facts when a document is attached.
- **🛠️ Multi-Tool Agent Routing**:
  - **PDF RAG Search Tool**: Semantic lookup across uploaded documents.
  - **Wikipedia Search Tool**: Real-time encyclopedia query lookup.
  - **Attendance Calculator Tool**: Calculates attendance percentages, shortfall, and safe skips for classes.
- **🔐 JWT Authentication & SQLite Database**:
  - Secure registration, password hashing (`werkzeug.security`), and JWT tokens.
  - Role-Based Access Control (`user` vs `admin`).
- **👑 Dedicated Admin Portal**:
  - Logging in as `admin` automatically opens a users management portal.
  - Search and filter registered users by ID, username, email, or role.
  - Separated from the chat view for data governance.
- **🎨 Modern Zero-Sidebar Web UI & Desktop App**:
  - **Web Application**: Sleek Cosmic Obsidian & Radiant Indigo theme, glassmorphism, dynamic user greetings, and pin attachment button.
  - **Desktop Application**: Optional native GUI built with CustomTkinter.

---

## 🏗️ Project Architecture

```
├── app.py                     # Flask web server, API routes, JWT auth & upload handling
├── auth.py                    # JWT token generation, verification, and decorators
├── database.py                # SQLite user management and admin seeding
├── config.py                  # Model definitions, RAG chunking parameters, and prompts
├── backend/
│   ├── agent_engine.py        # Intent detection, tool execution, and prompt routing
│   ├── llm_engine.py          # Ollama ChatLLM connection and model management
│   ├── memory_engine.py       # LangChain conversation buffer memory
│   ├── rag_engine.py          # Document loading, FAISS indexing, embedding warmup, search
│   └── tools/
│       ├── attendance_tool.py # Class attendance calculator tool
│       ├── pdf_rag_tool.py    # LangChain tool wrapper for vector retrieval
│       └── wikipedia_tool.py  # Wikipedia search tool wrapper
├── templates/
│   └── index.html             # Single-page web application (User Chat & Admin Portal)
├── static/
│   ├── css/style.css          # Modern Cosmic Dark & Radiant Indigo stylesheet
│   └── js/app.js              # Frontend client application logic
├── ui/                        # Native Desktop UI built with CustomTkinter
│   ├── main_window.py
│   ├── styles.py
│   └── components/
├── tests/                     # Unit tests for backend & RAG pipeline
├── uploads/                   # Upload directory for PDF documents (.gitignore protected)
└── requirements.txt           # Python package dependencies
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.12)
- **Ollama** installed and running on your machine: [ollama.com](https://ollama.com/)

Download and start your preferred model:
```bash
ollama pull llama3.2
```

### 2. Clone the Repository
```bash
git clone https://github.com/vignesh059/ollama-langchain-rag-assistant.git
cd ollama-langchain-rag-assistant
```

### 3. Create a Virtual Environment & Install Dependencies
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Run the Application

#### Option A: Web Interface (Flask)
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

#### Option B: Desktop Interface (CustomTkinter)
```bash
python ui/main_window.py
```

---

## 🔑 Default Credentials

- **Admin Account**:
  - **Username**: `admin`
  - **Password**: `adminpassword`
  - *(Accesses the Admin Users Portal directly)*
- **User Account**:
  - Use the **Create Account** tab on the login screen to register your own username and email.

---

## 🧪 Running Tests

Verify the backend and RAG pipeline integrity:
```bash
# Run backend & tool tests
python -m unittest tests/test_backend.py

# Run RAG vector search tests
python -m unittest tests/test_pdf_rag.py
```

---

## 📜 License
This project is open-source under the MIT License.
