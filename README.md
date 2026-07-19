# MedFlow

AI-powered healthcare platform that automates medical document processing using
OCR, NLP, and Retrieval-Augmented Generation (RAG) to extract clinical
insights, generate patient summaries, and recommend appropriate specialists.

## Stack

| Layer | Tech |
|---|---|
| Frontend | React, Vite, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, SQLite, JWT auth |
| AI | Google Gemini (free tier), LangChain, ChromaDB, Sentence Transformers, spaCy, Tesseract OCR, PyMuPDF |
| Deployment | Vercel (frontend), Render (backend) |

## How a document flows through the system

1. **Upload** — a PDF or image is uploaded against a patient record.
2. **OCR** — `PyMuPDF` extracts text directly from text-native PDF pages;
   any page that comes back mostly empty (i.e. it's a scan) is rasterized
   and run through `Tesseract` instead.
3. **NLP** — `spaCy` pulls out people, dates, organizations, and a
   keyword-based pass flags conditions/medications; a rule-based classifier
   tags the document type (lab report, prescription, etc).
4. **Embed & store** — the text is chunked and embedded with a local
   `sentence-transformers` model, then upserted into `ChromaDB`, namespaced
   by patient so retrieval never crosses patients.
5. **Summarize & triage** — `Gemini` (via `google-generativeai`, orchestrated
   with `LangChain` prompt templates) generates a plain-language summary and
   recommends a specialist.
6. **Ask questions** — the chat endpoint embeds the question, retrieves the
   nearest chunks from Chroma for that patient, and asks Gemini to answer
   using only that retrieved context (the RAG loop).

## Local setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

cp .env.example .env
# then edit .env and add your free Gemini API key from
# https://aistudio.google.com/app/apikey

uvicorn app.main:app --reload
```

The API will be live at `http://localhost:8000` (interactive docs at `/docs`).

You'll also need Tesseract installed system-side for scanned-document OCR:
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt install tesseract-ocr`
- Windows: install from https://github.com/UB-Mannheim/tesseract/wiki and set
  `TESSERACT_CMD` in `.env` to the installed `tesseract.exe` path.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app will be live at `http://localhost:5173`.

## Deployment

### Backend → Render

1. Push this repo to GitHub.
2. In Render, create a new Web Service pointing at the `backend/` directory
   (or use the included `render.yaml` as a Blueprint).
3. Set the `GEMINI_API_KEY` environment variable in the Render dashboard
   (it's marked `sync: false` in `render.yaml` so it isn't committed).
4. Update `CORS_ORIGINS` to your deployed frontend URL once you have it.

Note: Render's free tier has an ephemeral filesystem, so uploaded files and
the SQLite/Chroma data will reset on redeploy/restart. For a production
deployment, move to a persistent disk or managed Postgres + a hosted vector
DB (e.g. Chroma Cloud, Pinecone).

### Frontend → Vercel

1. Import the repo in Vercel, set the root directory to `frontend/`.
2. Set the environment variable `VITE_API_URL` to your deployed Render URL.
3. Deploy — `vercel.json` is already configured for SPA routing.

## Project structure

```
medflow/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + startup
│   │   ├── core/               # config, JWT/security
│   │   ├── db/                 # SQLAlchemy session
│   │   ├── models/              # ORM models
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── routers/               # auth, patients, documents, chat
│   │   └── services/                # ocr, nlp, embeddings, vectorstore, rag
│   ├── requirements.txt
│   └── render.yaml
└── frontend/
    ├── src/
    │   ├── api/                 # axios client + typed endpoint functions
    │   ├── context/              # AuthContext
    │   ├── components/            # Navbar, PatientCard, DocumentList, ChatBox
    │   ├── pages/                   # Login, Register, Dashboard, PatientDetail
    │   └── types/
    └── vercel.json
```

## Notes on the "free tools" constraint

- **Gemini** free tier (`gemini-1.5-flash`) handles all generation — summaries,
  specialist recommendations, and RAG answers.
- **Sentence Transformers** (`all-MiniLM-L6-v2`) runs locally for embeddings —
  no API cost, no rate limit.
- **ChromaDB** runs embedded/persistent on disk — no hosted service needed
  for development.
- **spaCy** (`en_core_web_sm`) and **Tesseract**/**PyMuPDF** are all open
  source and run locally.

The one paid-adjacent dependency is Gemini API usage beyond the free tier's
rate limits — monitor usage in Google AI Studio if you scale up.
