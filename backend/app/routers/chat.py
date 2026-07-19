from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.models import Patient, ChatMessage, User
from app.schemas.schemas import ChatQuery, ChatResponse, ChatMessageOut
from app.services import rag

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
def ask_question(payload: ChatQuery, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.id == payload.patient_id, Patient.owner_id == user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = rag.answer_patient_question(payload.patient_id, payload.question)

    db.add(ChatMessage(patient_id=payload.patient_id, role="user", content=payload.question))
    db.add(ChatMessage(patient_id=payload.patient_id, role="assistant", content=result["answer"]))
    db.commit()

    return ChatResponse(answer=result["answer"], sources=result["sources"])


@router.get("/history/{patient_id}", response_model=list[ChatMessageOut])
def get_chat_history(patient_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.owner_id == user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return (
        db.query(ChatMessage)
        .filter(ChatMessage.patient_id == patient_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
