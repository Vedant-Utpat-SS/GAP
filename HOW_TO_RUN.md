# How to Run — Contract Analysis (GAP)

This guide covers how to set up and run the **Backend** (Python FastAPI) and **Frontend** (React + Vite).

---

## Prerequisites

| Tool       | Version  | Check command        |
| ---------- | -------- | -------------------- |
| Python     | 3.10+    | `python --version`   |
| Node.js    | 18+      | `node --version`     |
| npm        | 9+       | `npm --version`      |
| pip        | latest   | `pip --version`      |

---

## 1. Environment Variable

The project uses the **Google Gemini API** for embeddings and chat. You need a `GOOGLE_API_KEY`.

1. Get a free key at https://aistudio.google.com/apikey
2. Set it in your environment:

**Windows (PowerShell)**
```powershell
$env:GOOGLE_API_KEY = "your_key_here"
```

**Windows (CMD)**
```cmd
set GOOGLE_API_KEY=your_key_here
```

**Linux / macOS**
```bash
export GOOGLE_API_KEY=your_key_here
```

**Or** create a `.env` file inside `GAP/UI/`:
```
GOOGLE_API_KEY=your_key_here
```

---

## 2. Backend Setup (Python FastAPI)

The backend lives in `GAP/UI/Backend.py` and runs on **http://localhost:8000**.

### 2.1 Install Python Dependencies

Open a terminal and navigate to the project root (`GAP/`):

```bash
cd GAP
```

Install the required packages:

```bash
pip install fastapi uvicorn langchain langchain-community langchain-google-genai langchain-text-splitters chromadb pypdf pydantic
```

### 2.2 Add Documents

Place your PDF/DOC/DOCX contract files in the `GAP/UI/data/` folder. These will be loaded into the vector database on server startup.

### 2.3 Start the Backend

```bash
cd GAP/UI
python Backend.py
```

You should see:

```
[INFO] Loading documents into Chroma …
[INFO] Chroma ready.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Backend API Endpoints

| Method | URL      | Body                    | Description                        |
| ------ | -------- | ----------------------- | ---------------------------------- |
| POST   | `/query` | `{ "query": "..." }`   | Send a question, get a RAG answer  |
| GET    | `/files` | —                       | List uploaded document filenames   |

---

## 3. Frontend Setup (React + Vite)

The frontend lives in `GAP/UI/` and runs on **http://localhost:5173**.

### 3.1 Install Node Dependencies

Open a **new terminal** and navigate to the UI directory:

```bash
cd GAP/UI
npm install
```

### 3.2 (Optional) Configure API URL

By default the frontend connects to `http://localhost:8000`. To change this, create a `.env` file in `GAP/UI/`:

```
VITE_API_URL=http://localhost:8000
```

### 3.3 Start the Frontend

```bash
npm run dev
```

You should see:

```
VITE v8.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://0.0.0.0:5173/
```

Open **http://localhost:5173** in your browser.

---

## 4. Quick Start (Both Together)

You need **two terminals** running simultaneously:

**Terminal 1 — Backend:**
```bash
cd GAP/UI
python Backend.py
```

**Terminal 2 — Frontend:**
```bash
cd GAP/UI
npm install   # only needed the first time
npm run dev
```

Then open http://localhost:5173 in your browser and start querying your contracts.

---

## 5. Reset the Vector Database

If you need to clear and rebuild the ChromaDB vector store:

```bash
cd GAP
python -m RAG.populate_database --reset
```

---

## 6. Troubleshooting

| Problem                              | Solution                                                              |
| ------------------------------------ | --------------------------------------------------------------------- |
| `GOOGLE_API_KEY not set`             | Set the env variable or add it to `GAP/UI/.env`                       |
| `ModuleNotFoundError: No module ...` | Run `pip install` with all dependencies listed in section 2.1         |
| Backend port 8000 already in use     | Kill the process using that port or change the port in `Backend.py`   |
| Frontend can't reach backend         | Make sure the backend is running first on port 8000                   |
| No documents found                   | Place PDF/DOC/DOCX files in `GAP/UI/data/`                           |
| `npm install` fails                  | Delete `node_modules/` and `package-lock.json`, then retry            |

---

## Project Structure Overview

```
GAP/
├── RAG/                        # Core RAG logic
│   ├── get_embedding_function.py   # Google Gemini embeddings
│   ├── populate_database.py        # Load PDFs into ChromaDB
│   └── query_data.py               # Query the vector DB + LLM
├── UI/                         # Full-stack application
│   ├── Backend.py                  # FastAPI server (port 8000)
│   ├── data/                       # Place contract PDFs here
│   ├── chroma/                     # ChromaDB storage (auto-created)
│   ├── src/                        # React frontend source
│   │   ├── App.jsx
│   │   ├── components/Chat/        # Chat UI components
│   │   ├── pages/                  # Page components
│   │   └── services/api.js         # API client (calls backend)
│   ├── package.json                # Node.js dependencies
│   └── vite.config.js              # Vite dev server config
└── HOW_TO_RUN.md               # ← This file
```
