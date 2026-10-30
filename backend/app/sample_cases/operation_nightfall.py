import hashlib
from datetime import datetime
from typing import List
from ..schemas import EvidenceItem, EvidenceType, AudioSegment

def get_operation_nightfall_case() -> List[EvidenceItem]:
    """
    Returns a pre-loaded, high-fidelity sample forensic case:
    'Operation Nightfall: The Vance Discrepancy'
    Featuring 4 pieces of cross-contradicting multimodal evidence.
    """
    
    # 1. Audio Transcript from Suspect Interrogation
    audio_text = (
        "[00:05 - 00:18] Detective Chen: State your full name and where you were on the night of October 14th.\n"
        "[00:19 - 00:45] Marcus Vance: My name is Marcus Vance. On October 14th, I never left Chicago. I was having dinner with business associates at Le Petit Bistro on Michigan Avenue from 7:30 PM until nearly 10:15 PM.\n"
        "[00:46 - 01:02] Detective Chen: Did you take any domestic or commercial flights out of Illinois that evening?\n"
        "[01:03 - 01:21] Marcus Vance: Absolutely not. I had back-to-back meetings in Chicago all afternoon, followed by dinner. My car was parked at the hotel in downtown Chicago all night."
    )
    audio_hash = hashlib.sha256(audio_text.encode()).hexdigest()
    
    item_audio = EvidenceItem(
        id="EV-001",
        filename="audio_interrogation_vance.wav",
        evidence_type=EvidenceType.AUDIO,
        sha256_hash=audio_hash,
        file_size_bytes=3420184,
        extracted_text=audio_text,
        audio_segments=[
            AudioSegment(start=5.0, end=18.0, text="Detective Chen: State your full name and where you were on the night of October 14th."),
            AudioSegment(start=19.0, end=45.0, text="Marcus Vance: On October 14th, I never left Chicago. I was having dinner at Le Petit Bistro from 7:30 PM until 10:15 PM."),
            AudioSegment(start=46.0, end=62.0, text="Detective Chen: Did you take any domestic flights out of Illinois?"),
            AudioSegment(start=63.0, end=81.0, text="Marcus Vance: Absolutely not. I had meetings in Chicago all afternoon.")
        ],
        metadata={"duration_seconds": 81.0, "format": "wav", "source_device": "Sony ICD-TX660 Voice Recorder"},
        uploaded_at="2026-10-15T09:30:00Z"
    )

    # 2. Airline Manifest Document
    flight_text = (
        "AMERICAN AIRLINES PASSENGER RECONCILIATION LOG\n"
        "FLIGHT NUMBER: AA-492 (Non-stop)\n"
        "DEPARTURE: Chicago O'Hare (ORD) - Scheduled: 4:15 PM (Actual: 4:22 PM), October 14th\n"
        "ARRIVAL: Dallas Fort Worth (DFW) - Scheduled: 6:45 PM (Actual: 6:51 PM), October 14th\n"
        "------------------------------------------------------------------------------------\n"
        "PASSENGER: VANCE, MARCUS\n"
        "SEAT: 04B (First Class)\n"
        "TICKET NUMBER: 001-8291039912\n"
        "GATE BOARDING SCAN: ORD Gate K12 at 4:02 PM CST (Verified biometric/ID match)\n"
        "BAGGAGE TAG: AA-88219 (1 Checked Priority Bag, Claimed at DFW Carousel 3 at 7:08 PM)"
    )
    flight_hash = hashlib.sha256(flight_text.encode()).hexdigest()
    item_flight = EvidenceItem(
        id="EV-002",
        filename="flight_manifest_aa492.pdf",
        evidence_type=EvidenceType.DOCUMENT,
        sha256_hash=flight_hash,
        file_size_bytes=142800,
        extracted_text=flight_text,
        metadata={"pages": 1, "document_type": "TSA/Airline Certified Passenger Manifest"},
        uploaded_at="2026-10-15T11:15:00Z"
    )

    # 3. Hotel Security Access Log
    hotel_text = (
        "DALLAS GRAND CONTINENTAL HOTEL - ELECTRONIC ACCESS & CCTV EVENT LOG\n"
        "DATE: October 14th\n"
        "------------------------------------------------------------------------------------\n"
        "19:42:15 CST - Valet Parking: Black Lincoln Navigator (TX Lic: 7BV-K82) received from Driver: M. Vance.\n"
        "20:04:10 CST - Lobby Front Desk: Room 402 Keycard issued to Marcus Vance.\n"
        "20:12:35 CST - CCTV Cam #4 (4th Floor Corridor): Subject matching Marcus Vance entered Room 402 carrying dark duffel.\n"
        "21:18:00 CST - Room 402 Minibar Sensor: 1x Sparking Water accessed.\n"
        "22:30:12 CST - Room 402 Lock: Master keycard deadlock engaged from interior."
    )
    hotel_hash = hashlib.sha256(hotel_text.encode()).hexdigest()
    item_hotel = EvidenceItem(
        id="EV-003",
        filename="dallas_hotel_surveillance_log.txt",
        evidence_type=EvidenceType.DOCUMENT,
        sha256_hash=hotel_hash,
        file_size_bytes=48210,
        extracted_text=hotel_text,
        metadata={"system": "Onity Electronic Lock System v4.1", "location": "Dallas, TX"},
        uploaded_at="2026-10-15T14:00:00Z"
    )

    # 4. Mobile Phone Cellebrite Chat Extraction
    chat_text = (
        "CELLEBRITE UFED EXTRACTION REPORT: APN DEVICE ID #88921\n"
        "APPLICATION: Signal Encrypted Messenger (Database Decryption)\n"
        "CHAT THREAD: Marcus Vance <-> 'Ghost Contact'\n"
        "------------------------------------------------------------------------------------\n"
        "[Oct 14, 15:45 CST] Marcus: Heading to ORD now. Meeting the courier tonight at the hotel in Dallas.\n"
        "[Oct 14, 18:55 CST] Marcus: Just landed at DFW. Getting bag and Uber.\n"
        "[Oct 14, 20:45 CST] Marcus: Package secured in Dallas room 402. Don't call this burner again.\n"
        "[Oct 14, 20:47 CST] Ghost Contact: Understood. Transfer of $250,000 sent to the Cayman escrow."
    )
    chat_hash = hashlib.sha256(chat_text.encode()).hexdigest()
    item_chat = EvidenceItem(
        id="EV-004",
        filename="signal_cellebrite_extraction.txt",
        evidence_type=EvidenceType.DOCUMENT,
        sha256_hash=chat_hash,
        file_size_bytes=31200,
        extracted_text=chat_text,
        metadata={"extraction_type": "Physical Dump", "device": "iPhone 15 Pro", "imei": "358912098412948"},
        uploaded_at="2026-10-16T08:00:00Z"
    )

    return [item_audio, item_flight, item_hotel, item_chat]

