"""
Embedding generation using Google's Gemini embedding API.

We deliberately use Gemini's hosted embedding endpoint here instead of a local
sentence-transformers model. Loading sentence-transformers pulls in torch,
which is memory-heavy - on constrained hosts (e.g. free-tier Render's 512MB
RAM limit) loading torch alongside spaCy and ChromaDB during document
processing can exceed available memory and crash the instance. Using Gemini's
API instead means no large ML library needs to be loaded into memory at all;
the tradeoff is that embedding calls now require network access and count
against Gemini's free-tier rate limits.
"""
from app.core.config import get_settings

settings = get_settings()

_client = None

EMBEDDING_MODEL = "text-embedding-004"  # Gemini's free embedding model


def _get_client():
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Get a free key at "
                "https://aistudio.google.com/app/apikey and add it to your .env"
            )
        from google import genai  # lazy import - keeps app startup fast/light
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts one at a time via the Gemini API.
    (Simple loop rather than a batch call - keeps this robust across SDK
    versions and easy to reason about for a handful of chunks per document.)"""
    client = _get_client()
    embeddings = []
    for text in texts:
        result = client.models.embed_content(model=EMBEDDING_MODEL, contents=text)
        embeddings.append(result.embeddings[0].values)
    return embeddings


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Simple sliding-window chunker on characters. Good enough for clinical
    notes; swap for a token-aware splitter (e.g. LangChain's
    RecursiveCharacterTextSplitter) if you need tighter control."""
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks