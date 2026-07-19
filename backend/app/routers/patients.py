from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.models import Patient, User
from app.schemas.schemas import PatientCreate, PatientUpdate, PatientOut

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post("", response_model=PatientOut, status_code=201)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient = Patient(owner_id=user.id, **payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("", response_model=list[PatientOut])
def list_patients(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Patient).filter(Patient.owner_id == user.id).order_by(Patient.created_at.desc()).all()


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient = _get_owned_patient(patient_id, db, user)
    return patient


@router.patch("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: str, payload: PatientUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    patient = _get_owned_patient(patient_id, db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient = _get_owned_patient(patient_id, db, user)
    db.delete(patient)
    db.commit()


def _get_owned_patient(patient_id: str, db: Session, user: User) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.owner_id == user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
