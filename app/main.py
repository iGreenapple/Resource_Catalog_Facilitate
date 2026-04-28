"""Spouštěcí bod aplikace: vytváří FastAPI app a registruje endpointy."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.api.ai import router as ai_router
from app.api.resources import router as resources_router

load_dotenv(override=True)

app = FastAPI(title="FACILITATE Resource Catalogue MVP")

app.include_router(resources_router)
app.include_router(ai_router)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def landing_page():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}
