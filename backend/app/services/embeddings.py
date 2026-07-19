"""
Embedding generation using a free, local Sentence Transformers model.
No API cost - runs on CPU, good enough quality for a RAG retrieval step.

NOTE: sentence-transformers (and the torch it pulls in) is imported lazily,
inside get_model(), rather than at module level. Importing torch is heavy
(memory + time), and on constrained hosts (e.g. free-tier Render) importing
it eagerly at app startup can cause the app to blow past the platform's
startup timeout before it ever binds to a port. Deferring the import means
the app boots fast and only pays this cost the first time a document is
actually processed.
"""

_model = None

MODEL_NAME = "all-MiniLM-L6-v2"  # 384-dim, fast, free, good general baseline


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # lazy import - see note above
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
