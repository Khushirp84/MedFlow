"""
Thin wrapper around a persistent ChromaDB collection used for RAG retrieval.
Documents are namespaced by patient_id via metadata so a query for one
patient never leaks context from another.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings
from app.services.embeddings import embed_texts, embed_text, chunk_text

settings = get_settings()

_client = None
_collection = None

COLLECTION_NAME = "medflow_documents"


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_collection():
    global _collection
    if _collection is None:
        _collection = get_client().get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def add_document(document_id: str, patient_id: str, text: str, filename: str) -> int:
    """Chunk a document's text, embed each chunk, and upsert into Chroma.
    Returns the number of chunks stored."""
    chunks = chunk_text(text)
    if not chunks:
        return 0

    embeddings = embed_texts(chunks)
    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"patient_id": patient_id, "document_id": document_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]

    get_collection().upsert(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    return len(chunks)


def query_patient_documents(patient_id: str, question: str, n_results: int = 5) -> dict:
    """Retrieve the most relevant chunks for a question, scoped to one patient."""
    query_embedding = embed_text(question)
    results = get_collection().query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"patient_id": patient_id},
    )
    return results


def delete_document(document_id: str) -> None:
    get_collection().delete(where={"document_id": document_id})
