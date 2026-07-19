from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth ----------

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    full_name: str
    email: EmailStr
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Patients ----------

class PatientCreate(BaseModel):
    full_name: str
    date_of_birth: str | None = None
    gender: str | None = None
    contact_info: str | None = None
    notes: str | None = None


class PatientUpdate(BaseModel):
    full_name: str | None = None
    date_of_birth: str | None = None
    gender: str | None = None
    contact_info: str | None = None
    notes: str | None = None


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    full_name: str
    date_of_birth: str | None
    gender: str | None
    contact_info: str | None
    notes: str | None
    created_at: datetime


# ---------- Documents ----------

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    patient_id: str
    filename: str
    doc_type: str
    summary: str | None
    recommended_specialist: str | None
    status: str
    created_at: datetime


class DocumentDetailOut(DocumentOut):
    raw_text: str | None
    entities_json: str | None


# ---------- Chat / RAG ----------

class ChatQuery(BaseModel):
    patient_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str
    created_at: datetime
