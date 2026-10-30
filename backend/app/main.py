import os
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from .config import UPLOAD_DIR, BASE_DIR
from .schemas import (
    EvidenceItem,
    EvidenceType,
    ForensicAnalysisReport,
    AirGapStatus
)
from .services.airgap_monitor import AirGapMonitor
from .services.document_engine import DocumentEngine
from .services.audio_engine import AudioEngine
from .services.forensic_analyzer import ForensicAnalyzer
from .services.llm_engine import LLMEngine
from .sample_cases.operation_nightfall import get_operation_nightfall_case

app = FastAPI(
    title="AegisDesk - Air-Gapped Forensic Investigator",
    description="Offline multimodal intelligence and contradiction discovery platform.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session evidence store
ACTIVE_EVIDENCE: Dict[str, EvidenceItem] = {}

# Populate with default sample case on startup
for item in get_operation_nightfall_case():
    ACTIVE_EVIDENCE[item.id] = item

@app.get("/api/status")
async def get_system_status() -> Dict[str, Any]:
    """Returns real-time air-gap network status, hardware telemetry, and local LLM availability."""
    airgap = AirGapMonitor.check_network_isolation()
    ollama_online = await LLMEngine.is_ollama_available()
    models = await LLMEngine.list_available_models() if ollama_online else []

    return {
        "airgap_audit": airgap.model_dump(),
        "ollama_online": ollama_online,
        "available_models": models,
        "evidence_in_locker": len(ACTIVE_EVIDENCE),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/api/evidence")
async def list_evidence() -> List[EvidenceItem]:
    """Returns all evidence items currently in the locker."""
    return list(ACTIVE_EVIDENCE.values())

@app.post("/api/reset-sample")
async def reset_sample() -> List[EvidenceItem]:
    """Resets the evidence locker to the verified Operation Nightfall case."""
    ACTIVE_EVIDENCE.clear()
    for item in get_operation_nightfall_case():
        ACTIVE_EVIDENCE[item.id] = item
    return list(ACTIVE_EVIDENCE.values())

@app.post("/api/upload")
async def upload_evidence(file: UploadFile = File(...)) -> EvidenceItem:
    """
    Accepts evidence file (.pdf, .txt, .wav, .mp3, etc.), writes to local disk,
    calculates SHA-256 for chain of custody, and extracts text/audio.
    """
    ev_id = f"EV-{uuid.uuid4().hex[:6].upper()}"
    ext = Path(file.filename).suffix.lower()
    save_path = UPLOAD_DIR / f"{ev_id}_{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(save_path)
    sha256_hash = AirGapMonitor.calculate_sha256(str(save_path))

    # Detect evidence type
    if ext in [".wav", ".mp3", ".m4a", ".ogg", ".flac"]:
        ev_type = EvidenceType.AUDIO
        text, segments, meta = AudioEngine.transcribe(str(save_path))
    elif ext in [".pdf", ".txt", ".log", ".csv", ".json", ".md"]:
        ev_type = EvidenceType.DOCUMENT
        text, meta = DocumentEngine.extract_text_from_file(str(save_path))
        segments = None
    else:
        ev_type = EvidenceType.DOCUMENT
        text, meta = DocumentEngine.extract_text_from_file(str(save_path))
        segments = None

    item = EvidenceItem(
        id=ev_id,
        filename=file.filename,
        evidence_type=ev_type,
        sha256_hash=sha256_hash,
        file_size_bytes=file_size,
        extracted_text=text,
        audio_segments=segments,
        metadata=meta,
        uploaded_at=datetime.utcnow().isoformat() + "Z"
    )

    ACTIVE_EVIDENCE[item.id] = item
    return item

@app.post("/api/analyze")
async def run_analysis() -> ForensicAnalysisReport:
    """
    Executes cross-examination across all evidence in the locker.
    Generates Contradiction Matrix, Timeline, and Entity Graph.
    """
    if not ACTIVE_EVIDENCE:
        raise HTTPException(status_code=400, detail="Evidence locker is empty. Upload files first.")

    evidence_list = list(ACTIVE_EVIDENCE.values())
    report = await ForensicAnalyzer.analyze_case(
        case_id="CASE-2026-NIGHTFALL",
        case_name="Operation Nightfall - Discrepancy Matrix",
        evidence_items=evidence_list
    )
    return report

# Mount Frontend static files
FRONTEND_DIR = BASE_DIR.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

