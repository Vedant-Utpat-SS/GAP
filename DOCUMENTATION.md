# GAP — Contract Analysis Platform

## Overview

**GAP (Generative AI Platform)** is an AI-powered contract analysis tool that allows users to upload legal/business documents (PDF, DOC, DOCX) and ask natural language questions about them. It uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-grounded answers by combining vector-based document search with Google's Gemini LLM.

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                          USER (Browser)                              │
│                     http://localhost:5173                             │
└────────────────────────────┬─────────────────────────────────────────┘
                             │  HTTP (REST API)
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                          │
│                                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  ┌───────────┐  │
│  │ App.jsx     │→ │ContractAnaly-│  │ ChatWindow │  │ api.js    │  │
│  │ (entry)     │  │sis.jsx       │  │ ChatInput  │  │ (service) │  │
│  │             │  │ (main page)  │  │ ChatMessage│  │           │  │
│  └─────────────┘  └──────────────┘  └────────────┘  └─────┬─────┘  │
│                                                            │        │
└────────────────────────────────────────────────────────────┼────────┘
                                                             │
                        POST /query  &  GET /files           │
                                                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Uvicorn)                        │
│                     http://localhost:8000                             │
│                                                                      │
│  Backend.py                                                          │
│  ├── POST /query   → calls RAG pipeline → returns AI answer         │
│  └── GET  /files   → lists documents in data/ folder                │
│                                                                      │
│  On Startup (lifespan):                                              │
│  └── populate_database.load()  → loads docs into ChromaDB            │
└────────────────────┬───────────────────────────┬─────────────────────┘
                     │                           │
                     ▼                           ▼
┌────────────────────────────┐   ┌──────────────────────────────────────┐
│     ChromaDB (Vector DB)   │   │      Google Gemini API (Cloud)       │
│     Local SQLite storage   │   │                                      │
│     chroma/chroma.sqlite3  │   │  • Embedding: gemini-embedding-001   │
│                            │   │  • LLM:       gemini-2.5-flash-lite  │
└────────────────────────────┘   └──────────────────────────────────────┘
```

---

## Project Structure

```
GAP/
├── DOCUMENTATION.md            ← This file
├── README.md                   ← Quick-start notes
│
├── RAG/                        ← RAG (Retrieval-Augmented Generation) engine
│   ├── get_embedding_function.py   → Google Gemini embedding setup
│   ├── populate_database.py        → PDF loading, chunking, ChromaDB storage
│   ├── query_data.py               → Semantic search + LLM answer generation
│   └── test_rag.py                 → Automated RAG evaluation tests
│
├── UI/                         ← Full-stack web application
│   ├── .env                        → Environment variables (GOOGLE_API_KEY)
│   ├── Backend.py                  → FastAPI server (REST API)
│   ├── index.html                  → HTML entry point
│   ├── vite.config.js              → Vite dev server config
│   ├── package.json                → Node.js dependencies
│   ├── style.css                   → Legacy styles
│   ├── data/                       → Contract documents (PDF, DOC, DOCX)
│   ├── chroma/                     → ChromaDB persistent storage
│   ├── src/
│   │   ├── main.jsx                → React entry point
│   │   ├── App.jsx                 → Root component
│   │   ├── App.css                 → Main stylesheet (Sofdel CMP branding)
│   │   ├── index.css               → Global CSS reset
│   │   ├── pages/
│   │   │   └── ContractAnalysis.jsx → Main page (sidebar + chat layout)
│   │   ├── components/
│   │   │   └── Chat/
│   │   │       ├── ChatWindow.jsx  → Chat container, message history, quick-chips
│   │   │       ├── ChatInput.jsx   → Auto-resize textarea + send button
│   │   │       └── ChatMessage.jsx → Individual message bubble (user/AI)
│   │   └── services/
│   │       └── api.js              → HTTP client (sendMessage, fetchDocuments)
│   └── IL/                         → Intermediate layer (Express.js, unused)
│       ├── Backend.js
│       └── package.json
│
└── Unused_Components/          ← Legacy/experimental code
    ├── script.js
    ├── Send_Email.py
    ├── Tkinter_UI.py
    └── ui_merge.py
```

---

## Services & Technologies Used

### 1. Frontend — React + Vite

| Technology    | Purpose                                          |
|---------------|--------------------------------------------------|
| **React 19**  | Component-based UI framework                     |
| **Vite 8**    | Fast dev server with HMR (Hot Module Replacement) |
| **Inter Font**| UI typography (loaded from Google Fonts)          |
| **CSS Variables** | Theming with Sofdel CMP brand colors (#A50164) |

**Key Components:**

| Component                | Role                                                              |
|--------------------------|-------------------------------------------------------------------|
| `ContractAnalysis.jsx`   | Main page — sidebar with document list + chat area                |
| `ChatWindow.jsx`         | Chat container — manages messages, loading state, quick-action chips |
| `ChatInput.jsx`          | Auto-resizing textarea with Enter-to-send                         |
| `ChatMessage.jsx`        | Message bubble — distinct styles for user vs AI                   |
| `api.js`                 | Service layer — `sendMessage()` and `fetchDocuments()` API calls  |

### 2. Backend — FastAPI (Python)

| Technology     | Purpose                                              |
|----------------|------------------------------------------------------|
| **FastAPI**    | High-performance async Python web framework          |
| **Uvicorn**    | ASGI server running FastAPI                          |
| **Pydantic**   | Request/response validation (QueryRequest model)     |
| **CORS Middleware** | Allows cross-origin requests from Vite dev server |

**API Endpoints:**

| Method | Endpoint   | Request Body          | Response                        | Description                     |
|--------|------------|-----------------------|---------------------------------|---------------------------------|
| POST   | `/query`   | `{ "query": "..." }`  | `{ "answer": "..." }`          | Send a question to the RAG pipeline |
| GET    | `/files`   | —                      | `{ "files": ["doc1.pdf", ...] }` | List all uploaded contract documents |

**Startup Lifecycle:**
1. Load `.env` file → sets `GOOGLE_API_KEY` in environment
2. Add project root to `sys.path` for RAG module imports
3. On app startup → `populate_database.load()` indexes all documents into ChromaDB
4. Server listens on `http://0.0.0.0:8000`

### 3. RAG Pipeline (Retrieval-Augmented Generation)

The core intelligence layer, implemented in `RAG/`:

#### Step-by-step Flow:

```
  User Question
       │
       ▼
  ┌─────────────────────────────────────┐
  │  1. EMBED the question              │
  │     Google Gemini Embedding API     │
  │     model: gemini-embedding-001     │
  └──────────────┬──────────────────────┘
                 │
                 ▼
  ┌─────────────────────────────────────┐
  │  2. SEARCH ChromaDB                 │
  │     Similarity search (top 5)       │
  │     Returns most relevant chunks    │
  └──────────────┬──────────────────────┘
                 │
                 ▼
  ┌─────────────────────────────────────┐
  │  3. BUILD PROMPT                    │
  │     Inject retrieved context +      │
  │     user question into template     │
  └──────────────┬──────────────────────┘
                 │
                 ▼
  ┌─────────────────────────────────────┐
  │  4. GENERATE ANSWER                 │
  │     Google Gemini LLM               │
  │     model: gemini-2.5-flash-lite    │
  │     temperature: 0.2                │
  └──────────────┬──────────────────────┘
                 │
                 ▼
        AI Answer returned to user
```

#### RAG Modules:

| Module                      | Responsibility                                                         |
|-----------------------------|------------------------------------------------------------------------|
| `get_embedding_function.py` | Creates Google Gemini embedding function (`gemini-embedding-001`)       |
| `populate_database.py`      | Loads PDFs → splits into chunks (800 chars, 80 overlap) → stores in ChromaDB |
| `query_data.py`             | Embeds query → searches ChromaDB → builds prompt → calls Gemini LLM    |
| `test_rag.py`               | Automated tests to validate RAG answer accuracy                       |

### 4. ChromaDB (Vector Database)

| Property          | Value                           |
|-------------------|---------------------------------|
| **Type**          | Embedded vector database        |
| **Storage**       | Local SQLite (`chroma/chroma.sqlite3`) |
| **Embedding Model** | Google `gemini-embedding-001` |
| **Chunk Size**    | 800 characters                  |
| **Chunk Overlap** | 80 characters                   |
| **Search Strategy** | Similarity search, top-k=5   |

**Document ID Format:** `{source_file}:{page_number}:{chunk_index}`  
Example: `data/contract.pdf:3:2` = 3rd page, 2nd chunk

### 5. Google Gemini API

| Service          | Model                     | Purpose                            |
|------------------|---------------------------|------------------------------------|
| **Embeddings**   | `gemini-embedding-001`    | Convert text to vector embeddings  |
| **LLM (Chat)**   | `gemini-2.5-flash-lite`   | Generate answers from context      |

**Authentication:** Via `GOOGLE_API_KEY` in `.env` file, loaded at backend startup.

---

## Application Flow (End-to-End)

### On Application Startup:

```
1. Backend starts (python Backend.py)
   ├── Reads .env → loads GOOGLE_API_KEY
   ├── populate_database.load()
   │   ├── PyPDFDirectoryLoader reads all PDFs from data/
   │   ├── RecursiveCharacterTextSplitter chunks the text
   │   ├── Google Gemini generates embeddings for each chunk
   │   └── ChromaDB stores vectors (skips already-indexed docs)
   └── Uvicorn serves API on http://localhost:8000

2. Frontend starts (npm run dev)
   └── Vite serves React app on http://localhost:5173
```

### User Interaction Flow:

```
1. User opens http://localhost:5173
   └── ContractAnalysis.jsx loads
       └── fetchDocuments() → GET /files → sidebar populates with 9 contracts

2. User selects a document from sidebar (optional)
   └── Active document highlighted, name shown in banner

3. User types a question (or clicks a quick-action chip)
   └── ChatInput.jsx captures input
       └── ChatWindow.jsx prepends "[Document: filename]" if doc selected
           └── api.js sendMessage() → POST /query { "query": "..." }

4. Backend processes the query
   ├── query_data.query_rag() called
   │   ├── Embeds question via Gemini
   │   ├── Searches ChromaDB for top 5 similar chunks
   │   ├── Constructs prompt: context + question
   │   └── Calls Gemini 2.5 Flash Lite for answer
   └── Returns { "answer": "..." }

5. Frontend displays the AI response
   └── ChatMessage.jsx renders the answer bubble
```

---

## Documents Loaded

The system currently has **9 contract documents** in `UI/data/`:

| # | Document |
|---|----------|
| 1 | ABC Company - Change Request (CR_02) Agreement.pdf |
| 2 | XYZ Formal Proposal for BBU Redesign and Development v1.docx |
| 3 | SmartProfessionalServicesAgreement.SSUSA.21oct22 - Comments.doc |
| 4 | Softdel - Formal Proposal for On-Premise Patlite Application Development v1.2.docx |
| 5 | Softdel - Formal SOW for IOT Sensor Cloud Platform - MVP Phase v1.0.docx |
| 6 | Softdel - Formal Proposal for Reduced Cost Android Display (RCAD) v2.0.docx |
| 7 | Softdel - Proposal Pre-Cert Dumb Electric v1.1.docx |
| 8 | SS USA Inc. - Protein Energy Storage LLC Master Service Agreement (MSA) v1.0.docx |
| 9 | SS USA Inc. - SOW for Bootloader and Firmware Upgrade Implementation v1.0.docx |

**Total chunks in ChromaDB:** 36

---

## How to Run

### Prerequisites
- Python 3.12+
- Node.js 18+
- Google API Key (get free at https://aistudio.google.com/apikey)

### 1. Set up environment
```bash
# In GAP/UI/.env
GOOGLE_API_KEY=your_api_key_here
```

### 2. Install Python dependencies
```bash
pip install fastapi uvicorn langchain-community langchain-core langchain-google-genai langchain-text-splitters chromadb pypdf
```

### 3. Install frontend dependencies
```bash
cd GAP/UI
npm install
```

### 4. Start Backend
```bash
cd GAP/UI
python Backend.py
# Starts on http://localhost:8000
```

### 5. Start Frontend
```bash
cd GAP/UI
npm run dev
# Starts on http://localhost:5173
```

---

## Prompt Template

The system uses the following prompt to ground answers in document context:

```
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
```

This ensures the LLM answers strictly from the retrieved document chunks, reducing hallucination.

---

## Quick-Action Chips (Pre-built Queries)

The chat UI offers these one-click prompts:

1. **Summarise this contract**
2. **What are the payment terms?**
3. **List all termination clauses**
4. **Key obligations of each party**
5. **Identify any risks or red flags**
6. **Who owns the intellectual property?**

---

## Tech Stack Summary

| Layer              | Technology                    | Version  |
|--------------------|-------------------------------|----------|
| Frontend Framework | React                         | 19.2     |
| Build Tool         | Vite                          | 8.0      |
| Backend Framework  | FastAPI                       | Latest   |
| ASGI Server        | Uvicorn                       | Latest   |
| Vector Database    | ChromaDB                      | Latest   |
| Embedding Model    | Google Gemini Embedding 001   | —        |
| LLM                | Google Gemini 2.5 Flash Lite  | —        |
| PDF Parsing        | PyPDF (via LangChain)         | Latest   |
| Text Splitting     | LangChain RecursiveCharacterTextSplitter | Latest |
| Orchestration      | LangChain Community + Core    | Latest   |
| Styling            | Custom CSS (Inter font)       | —        |
