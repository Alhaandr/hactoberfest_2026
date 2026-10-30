# 🛡️ AegisDesk: Air-Gapped Multimodal Forensic Investigator

> **An original, 100% offline intelligence workbench that cross-examines audio interrogations, scanned PDF documents, and surveillance logs to uncover perjury and timeline contradictions using open-weight AI.**

---

## 📌 The Problem
Investigative journalists, defense attorneys, corporate internal auditors, and whistleblower intake teams handle highly classified, sensitive evidence (wiretaps, leaked emails, flight manifests, interrogations).

Uploading this data to cloud-hosted proprietary LLMs (e.g., OpenAI, Anthropic, or Google Cloud) violates **legal privilege**, **confidentiality agreements (NDAs)**, and **GDPR/chain-of-custody protocols**.

**AegisDesk** proves that a coordinated pipeline of small, quantized **open-weight models** running entirely on consumer hardware can deliver high-precision forensic cross-examinations with **zero bytes leaking over the network**.

---

## 🚀 Key Features

* **🔒 Real-Time Air-Gap Monitor**: Actively monitors process socket descriptors (`psutil`) to certify zero external egress packets during analysis, printing a cryptographic verification certificate with every report.
* **🎙️ Local Audio Intelligence**: Transcribes audio interviews with sub-second timestamps locally using `faster-whisper` (CTranslate2 `int8` quantization) without sending sound bites to external APIs.
* **📄 Multimodal Document Ingestion**: Fast extraction of text, metadata, and timestamps from PDFs, Cellebrite mobile chat dumps, and CCTV sensor logs via `PyMuPDF`.
* **⚖️ Automated Contradiction Matrix**: Identifies alibi conflicts (e.g., suspect claiming to be at dinner in Chicago while boarding an American Airlines flight to Dallas) with side-by-side excerpt citations and severity scoring.
* **⏱️ Chronological Master Timeline**: Automatically aggregates, de-duplicates, and reconstructs a unified event timeline from disparate evidence files.
* **📜 Certified Forensic Dossier**: Generates a court-admissible audit document featuring SHA-256 chain-of-custody hashes for every piece of evidence.

---

## 🧠 Open-Source & Open-Weight AI Architecture

```
 ┌───────────────────────────────────────────────────────────────┐
 │                   AegisDesk Web Dashboard                     │
 │      Evidence Locker  |  Contradiction Matrix  |  Timeline    │
 └──────────────────────────────┬────────────────────────────────┘
                                │
 ┌──────────────────────────────▼────────────────────────────────┐
 │                      Forensic Core API                        │
 │        Chain-of-Custody Hashing  •  Air-Gap Socket Audit      │
 └──────┬───────────────────────┼─────────────────────────┬──────┘
        │                       │                         │
 ┌──────▼──────┐         ┌──────▼──────┐           ┌──────▼──────┐
 │ Audio Engine│         │Document Core│           │Reasoning SLM│
 │faster-whisper│        │   PyMuPDF   │           │  Llama 3.2  │
 │  (int8 CPU) │         │ (Text & Doc)│           │  via Ollama │
 └─────────────┘         └─────────────┘           └─────────────┘
```

1. **Reasoning & Cross-Examination**: Open-weight **Llama 3.2 (1B/3B)** or **Qwen 2.5 (3B)** running locally via Ollama with strict JSON schema constraints.
2. **Speech-to-Text**: Open-source **Whisper** via **`faster-whisper`** (CTranslate2 int8 CPU quantization), delivering sub-second transcription on standard dual-core laptops.
3. **Forensic Document Parsing**: Open-source **`PyMuPDF`** for zero-latency local PDF/text stream extraction.

---

## 📂 Pre-Loaded Demo: "Operation Nightfall"
AegisDesk includes a ready-to-test case with 4 conflicting evidence items:
1. `audio_interrogation_vance.wav` (Audio Transcript): Suspect Marcus Vance swears under oath he never left Chicago on Oct 14th and was dining at *Le Petit Bistro* from 7:30 PM to 10:15 PM.
2. `flight_manifest_aa492.pdf` (Flight Document): American Airlines manifest showing Marcus Vance boarded AA-492 First Class at O'Hare at 4:02 PM and landed in Dallas at 6:51 PM.
3. `dallas_hotel_surveillance_log.txt` (CCTV Log): Dallas Grand Hotel logs showing Marcus Vance checking into Room 402 at 8:12 PM with a duffel bag.
4. `signal_cellebrite_extraction.txt` (Encrypted Chat Dump): Signal chat where Vance texts a burner contact at 8:45 PM: *"Package secured in Dallas room 402."*

👉 **Result**: The engine instantly catches the alibi contradiction between Source 1 and Sources 2, 3, and 4, calculates the geographical impossibility, and reconstructs the timeline.

---

## ⚡ Quickstart

### Prerequisites
* Windows 10/11
* Python 3.11 (installed via `uv`)
* Ollama installed locally

### One-Click Launch
Double-click `start_aegisdesk.bat` in the project root:
```cmd
start_aegisdesk.bat
```
This automatically starts the local Ollama background server, boots the FastAPI application, and opens `http://127.0.0.1:8000` in your default browser.

### Manual Launch
```bash
# Activate virtual environment
.\backend\.venv\Scripts\activate

# Run FastAPI server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Navigate to: **`http://127.0.0.1:8000`**

---

## 🏆 Hackathon Presentation & Pitch Points
1. **Zero-Trust Privacy**: Demonstrate physical isolation—pull the Ethernet plug or turn off Wi-Fi on stage and watch the entire multimodal pipeline analyze audio, docs, and cross-reference contradictions with zero cloud calls.
2. **Lightweight Efficiency**: Show that a standard dual-core laptop without a dedicated GPU can run speech-to-text, document parsing, and SLM reasoning simultaneously.
3. **Court-Admissible Evidence Integrity**: Highlight the SHA-256 chain-of-custody hashing and active socket auditing, ensuring evidence has not been tampered with or leaked.

