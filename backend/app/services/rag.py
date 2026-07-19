"""
RAG orchestration layer. Uses Google's Gemini free tier as the generation
model, with ChromaDB + Sentence Transformers handling retrieval.

LangChain is used for prompt templating and the LLM wrapper; the retrieval
step itself queries our own vectorstore service directly since we already
have full control over chunking/metadata there.
"""
import json
from google import genai

from app.core.config import get_settings
from app.services.vectorstore import query_patient_documents

settings = get_settings()

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Get a free key at "
                "https://aistudio.google.com/app/apikey and add it to your .env"
            )
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


SUMMARY_PROMPT = """You are a clinical documentation assistant. Summarize the following
medical document for a busy clinician. Be concise, factual, and use plain language.
Include: chief findings, diagnoses mentioned, medications, and any follow-up actions noted.
Do not invent information that isn't in the text.

Document text:
---
{document_text}
---

Summary:"""

SPECIALIST_PROMPT = """You are a triage assistant. Based on the clinical document below,
recommend the single most appropriate medical specialist type (e.g. Cardiologist,
Endocrinologist, Neurologist, Orthopedist, Dermatologist, General Practitioner, etc.)
and a one-sentence justification. Respond ONLY as JSON:
{{"specialist": "...", "justification": "..."}}

Document text:
---
{document_text}
---
"""

QA_PROMPT = """You are a clinical assistant answering a question about a specific patient,
using only the retrieved document excerpts below as context. If the excerpts don't contain
enough information to answer confidently, say so rather than guessing.

Retrieved excerpts:
---
{context}
---

Question: {question}

Answer:"""


def summarize_document(document_text: str) -> str:
    client = _get_client()
    prompt = SUMMARY_PROMPT.format(document_text=document_text[:15_000])
    response = client.models.generate_content(model=settings.GEMINI_MODEL, contents=prompt)
    return response.text.strip()


def recommend_specialist(document_text: str) -> dict:
    client = _get_client()
    prompt = SPECIALIST_PROMPT.format(document_text=document_text[:15_000])
    response = client.models.generate_content(model=settings.GEMINI_MODEL, contents=prompt)
    raw = response.text.strip().strip("`").lstrip("json").strip()
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {"specialist": "General Practitioner", "justification": "Could not parse model output; defaulting."}


def answer_patient_question(patient_id: str, question: str) -> dict:
    """Full RAG loop: retrieve relevant chunks for this patient, then ask
    Gemini to answer using only that context."""
    results = query_patient_documents(patient_id, question)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "answer": "I couldn't find any relevant documents for this patient yet. "
                      "Try uploading and processing a document first.",
            "sources": [],
        }

    context = "\n\n---\n\n".join(documents)
    sources = sorted({m.get("filename", "unknown") for m in metadatas})

    client = _get_client()
    prompt = QA_PROMPT.format(context=context[:15_000], question=question)
    response = client.models.generate_content(model=settings.GEMINI_MODEL, contents=prompt)

    return {"answer": response.text.strip(), "sources": sources}