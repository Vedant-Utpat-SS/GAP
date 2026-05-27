# Debugging Guide — Contract Analysis (GAP)

A step-by-step guide to debug both the Backend and Frontend on any PC.

---

## Step 1: Clone / Copy the Project

Copy the entire `GAP/` folder to the target PC. The folder structure should be:

```
GAP/
├── RAG/
│   ├── get_embedding_function.py
│   ├── populate_database.py
│   └── query_data.py
├── UI/
│   ├── Backend.py
│   ├── package.json
│   ├── vite.config.js
│   ├── data/          ← place PDF/DOC/DOCX files here
│   └── src/           ← React frontend source
```

---

## Step 2: Verify Prerequisites

Open a terminal and run each command to confirm the tools are installed:

```powershell
python --version     # Need 3.10+
pip --version        # Need latest
node --version       # Need 18+
npm --version        # Need 9+
```

**If any command fails**, install the missing tool:
- Python: https://www.python.org/downloads/
- Node.js (includes npm): https://nodejs.org/

---

## Step 3: Set the API Key

The project needs a `GOOGLE_API_KEY` for Google Gemini.

**Option A — Environment variable (PowerShell):**
```powershell
$env:GOOGLE_API_KEY = "your_key_here"
```

**Option B — Environment variable (CMD):**
```cmd
set GOOGLE_API_KEY=your_key_here
```

**Option C — `.env` file (recommended):**
Create a file `GAP/UI/.env` with this content:
```
GOOGLE_API_KEY=your_key_here
```

> **How to verify:** `echo $env:GOOGLE_API_KEY` (PowerShell) or `echo %GOOGLE_API_KEY%` (CMD)

---

## Step 4: Install Python Dependencies

```powershell
pip install fastapi uvicorn langchain langchain-community langchain-google-genai langchain-text-splitters chromadb pypdf pydantic
```

**If you get permission errors**, use:
```powershell
pip install --user fastapi uvicorn langchain langchain-community langchain-google-genai langchain-text-splitters chromadb pypdf pydantic
```

### Verify installation:
```powershell
python -c "import fastapi; import uvicorn; import langchain; import chromadb; print('All Python packages OK')"
```

---

## Step 5: Add Documents

Place at least one `.pdf`, `.doc`, or `.docx` file in `GAP/UI/data/`.

```powershell
dir GAP\UI\data\
```

If the `data` folder is empty, the backend will start but queries will return no results.

---

## Step 6: Start the Backend

Open **Terminal 1**:

```powershell
cd GAP\UI
python Backend.py
```

### Expected output (success):
```
[INFO] Loading documents into Chroma …
[INFO] Chroma ready.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Debug — Common backend errors:

| Error Message | Cause | Fix |
|---|---|---|
| `GOOGLE_API_KEY not set` | API key not configured | See Step 3 |
| `ModuleNotFoundError: No module named 'fastapi'` | Missing Python package | Run `pip install fastapi uvicorn` |
| `ModuleNotFoundError: No module named 'langchain_google_genai'` | Missing package | Run `pip install langchain-google-genai` |
| `ModuleNotFoundError: No module named 'chromadb'` | Missing package | Run `pip install chromadb` |
| `ModuleNotFoundError: No module named 'RAG'` | Running from wrong directory | Must run from `GAP/UI/` |
| `Address already in use` | Port 8000 occupied | Kill the process: `netstat -ano | findstr :8000` then `taskkill /PID <PID> /F` |
| `[WARN] Could not load documents: ...` | PDF loading issue | Check files in `GAP/UI/data/` are valid PDFs |

### Verify the backend is running:

Open a browser and go to:
```
http://localhost:8000/docs
```
You should see the **FastAPI Swagger UI** with two endpoints (`/query` and `/files`).

Or test from PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/files"
```

Expected: `{"files": ["file1.pdf", ...]}`

---

## Step 7: Install Frontend Dependencies

Open **Terminal 2** (keep the backend running in Terminal 1):

```powershell
cd GAP\UI
npm install
```

### Expected output (success):
```
added 216 packages, and audited 217 packages in 2m
found 0 vulnerabilities
```

### Debug — Common npm errors:

| Error Message | Cause | Fix |
|---|---|---|
| `npm error code ENOENT ... package.json` | Wrong directory | Make sure you are in `GAP/UI/`, not the project root |
| `npm ERR! code EACCES` | Permission issue | Run terminal as Administrator |
| `node: command not found` | Node.js not installed | Install from https://nodejs.org/ |
| Dependency conflicts | Version mismatch | Delete `node_modules` and `package-lock.json`, then run `npm install` again |

---

## Step 8: Start the Frontend

Still in **Terminal 2**:

```powershell
npm run dev
```

### Expected output (success):
```
VITE v8.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://0.0.0.0:5173/
```

### Debug — Common frontend errors:

| Error Message | Cause | Fix |
|---|---|---|
| `'vite' is not recognized` | Dependencies not installed | Run `npm install` first |
| Port 5173 in use | Another process on that port | Kill it or change port in `vite.config.js` |
| CORS errors in browser console | Backend not running | Start the backend first (Step 6) |
| `Failed to fetch` in browser console | Backend not running or wrong URL | Check backend is on `http://localhost:8000` |

---

## Step 9: Test the Full Flow

1. Open **http://localhost:5173** in your browser
2. Type a question about your contracts (e.g., "Who is the director?")
3. You should get an AI-generated answer based on the uploaded documents

### Check the backend terminal — you should see request logs:
```
INFO:     127.0.0.1:xxxxx - "OPTIONS /query HTTP/1.1" 200 OK
INFO:     127.0.0.1:xxxxx - "POST /query HTTP/1.1" 200 OK
```

---

## Step 10: Debug from Another PC on the Network

The backend binds to `0.0.0.0`, so it's accessible on your local network.

### Find the host PC's IP:
```powershell
ipconfig
```
Look for the **IPv4 Address** (e.g., `10.5.0.34`).

### From the other PC, test:
```
http://<HOST_IP>:8000/docs
http://<HOST_IP>:8000/files
```

### If connection times out — open the firewall (run as Admin on host PC):
```powershell
New-NetFirewallRule -DisplayName "GAP Backend 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "GAP Frontend 5173" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow
```

### Connect frontend on another PC to this backend:
Create `GAP/UI/.env` on the other PC:
```
VITE_API_URL=http://<HOST_IP>:8000
```
Then run `npm run dev` on the other PC.

---

## Quick Debug Checklist

Use this checklist to quickly identify issues:

```
[ ] Python 3.10+ installed?             → python --version
[ ] Node.js 18+ installed?              → node --version
[ ] GOOGLE_API_KEY set?                  → echo $env:GOOGLE_API_KEY
[ ] Python packages installed?           → python -c "import fastapi, chromadb"
[ ] Documents in GAP/UI/data/?           → dir GAP\UI\data\
[ ] Running from correct directory?      → Should be in GAP\UI\
[ ] Backend running?                     → http://localhost:8000/docs
[ ] npm install done?                    → Check node_modules/ exists in GAP\UI\
[ ] Frontend running?                    → http://localhost:5173
[ ] Backend logs showing requests?       → Check Terminal 1 for POST /query logs
[ ] Firewall open? (remote debug only)   → Test-NetConnection <IP> -Port 8000
```

---

## Reset Everything (Clean Start)

If nothing works, start fresh:

```powershell
# 1. Reset the vector database
cd GAP\UI
Remove-Item -Recurse -Force chroma

# 2. Reinstall Node packages
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
npm install

# 3. Reinstall Python packages
pip install --force-reinstall fastapi uvicorn langchain langchain-community langchain-google-genai langchain-text-splitters chromadb pypdf pydantic

# 4. Start backend
python Backend.py

# 5. In another terminal, start frontend
cd GAP\UI
npm run dev
```
