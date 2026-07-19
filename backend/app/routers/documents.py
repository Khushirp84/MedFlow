import os
import json
import uuid
import traceback

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.models import Document, Patient, User
from app.schemas.schemas import DocumentOut, DocumentDetailOut
from app.core.config import get_settings
from app.services import ocr, nlp, vectorstore, rag

router = APIRouter(prefix="/api/documents", tags=["documents"])
settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


@router.post("/upload/{patient_id}", response_model=DocumentOut, status_code=201)
def upload_document(
    patient_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.owner_id == user.id)
        .first()
    )

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}",
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    stored_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_name)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    document = Document(
        patient_id=patient_id,
        filename=file.filename,
        file_path=file_path,
        status="pending",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    background_tasks.add_task(process_document, document.id)

    return document


def process_document(document_id: str):
    """
    Background processing pipeline.

    Flow:
    OCR
    ↓
    NLP
    ↓
    Classification
    ↓
    Vector Store
    ↓
    Gemini Summary
    ↓
    Specialist Recommendation
    """

    from app.db.database import SessionLocal

    db = SessionLocal()

    try:
        print("\n========== DOCUMENT PROCESSING START ==========")
        print("STEP 1 - Loading document")

        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            print("Document not found.")
            return

        document.status = "processing"
        db.commit()

        print("STEP 2 - OCR")
        text = ocr.extract_text_from_file(document.file_path)
        print(f"OCR Complete ({len(text)} characters)")

        print("STEP 3 - NLP Entity Extraction")
        entities = nlp.extract_entities(text)
        print("NLP Complete")

        print("STEP 4 - Document Classification")
        doc_type = nlp.classify_document_type(text)
        print(f"Document Type: {doc_type}")

        print("STEP 5 - Saving OCR Results")
        document.raw_text = text
        document.entities_json = json.dumps(entities)
        document.doc_type = doc_type
        db.commit()

        print("STEP 6 - Vector Store")
        vectorstore.add_document(
            document_id=document.id,
            patient_id=document.patient_id,
            text=text,
            filename=document.filename,
        )
        print("Vector Store Complete")

        try:
            print("STEP 7 - Gemini Summary")
            document.summary = rag.summarize_document(text)
            print("Gemini Summary Complete")

            print("STEP 8 - Specialist Recommendation")
            specialist_result = rag.recommend_specialist(text)
            document.recommended_specialist = specialist_result.get("specialist")
            print("Specialist Recommendation Complete")

        except RuntimeError as e:
            print("Gemini skipped:", e)
            document.summary = None
            document.recommended_specialist = None

        print("STEP 9 - Finalizing Document")

        document.status = "processed"
        db.commit()

        print("========== DOCUMENT PROCESSING COMPLETE ==========\n")

    except Exception as exc:
        print("\n========== DOCUMENT PROCESSING FAILED ==========")
        traceback.print_exc()
        print("PROCESSING ERROR:", exc)

        document = db.query(Document).filter(Document.id == document_id).first()

        if document:
            document.status = "failed"
            document.raw_text = f"Processing error: {exc}"
            db.commit()

    finally:
        db.close()


@router.get("/patient/{patient_id}", response_model=list[DocumentOut])
def list_patient_documents(
    patient_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.owner_id == user.id)
        .first()
    )

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return (
        db.query(Document)
        .filter(Document.patient_id == patient_id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get("/{document_id}", response_model=DocumentDetailOut)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return _get_owned_document(document_id, db, user)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    document = _get_owned_document(document_id, db, user)

    vectorstore.delete_document(document_id)

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()


def _get_owned_document(
    document_id: str,
    db: Session,
    user: User,
) -> Document:

    document = (
        db.query(Document)
        .join(Patient, Document.patient_id == Patient.id)
        .filter(
            Document.id == document_id,
            Patient.owner_id == user.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document