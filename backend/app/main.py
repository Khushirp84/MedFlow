from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.database import Base, engine
from app.models import models  # noqa: F401 - ensures models are registered before create_all
from app.routers import auth, patients, documents, chat

settings = get_settings()

app = FastAPI(
    title="MedFlow API",
    description="AI-powered healthcare document processing platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok", "service": "MedFlow API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
