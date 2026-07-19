"""
Embedding generation using a free, local Sentence Transformers model.
No API cost - runs on CPU, good enough quality for a RAG retrieval step.
"""
from sentence_transformers import SentenceTransformer

_model = None

MODEL_NAME = "all-MiniLM-L6-v2"  # 384-dim, fast, free, good general baseline


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return embeddings.tolist()


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
