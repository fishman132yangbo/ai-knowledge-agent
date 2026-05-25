from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat_api import router as chat_router
from api.document_api import router as document_router
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("BACKEND_CORS_ENV_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(chat_router,prefix="/api")
app.include_router(document_router,prefix="/api")
