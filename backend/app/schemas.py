from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EvidenceType(str, Enum):
    AUDIO = "audio"
    DOCUMENT = "document"
    IMAGE = "image"
    NOTE = "note"

class Severity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ContradictionCategory(str, Enum):
    ALIBI = "ALIBI"
    TIMELINE = "TIMELINE"
    LOCATION = "LOCATION"
    IDENTITY = "IDENTITY"
    FINANCIAL = "FINANCIAL"
    COMMUNICATION = "COMMUNICATION"

class AudioSegment(BaseModel):
    start: float
    end: float
    text: str

class EvidenceItem(BaseModel):
    id: str
    filename: str
    evidence_type: EvidenceType
    sha256_hash: str
    file_size_bytes: int
    extracted_text: str
    audio_segments: Optional[List[AudioSegment]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    uploaded_at: str

class ContradictionItem(BaseModel):
    id: str
    title: str
    description: str
    source_a_id: str
    source_a_name: str
    source_a_quote: str
    source_b_id: str
    source_b_name: str
    source_b_quote: str
    category: ContradictionCategory
    severity: Severity
    analysis_reasoning: str

class TimelineEvent(BaseModel):
    id: str
    timestamp_raw: str
    normalized_datetime: Optional[str] = None
    event_description: str
    source_id: str
    source_name: str
    entities: List[str] = Field(default_factory=list)
    confidence: float = 1.0

class EntityNode(BaseModel):
    name: str
    entity_type: str  # PERSON, LOCATION, ORGANIZATION, FLIGHT, DEVICE, ASSET
    mentions: int = 1
    sources: List[str] = Field(default_factory=list)

class AirGapStatus(BaseModel):
    is_airgapped: bool
    active_outbound_connections: int
    verification_message: str
    inspected_at: str

class ForensicAnalysisReport(BaseModel):
    case_id: str
    case_name: str
    summary: str
    evidence_count: int
    contradiction_count: int
    timeline_count: int
    entity_count: int
    contradictions: List[ContradictionItem]
    timeline: List[TimelineEvent]
    entities: List[EntityNode]
    airgap_audit: AirGapStatus
    analyzed_at: str
    model_used: str

