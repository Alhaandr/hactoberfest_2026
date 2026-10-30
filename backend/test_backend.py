import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path.parent))

from backend.app.schemas import EvidenceItem, EvidenceType
from backend.app.services.airgap_monitor import AirGapMonitor
from backend.app.services.forensic_analyzer import ForensicAnalyzer
from backend.app.sample_cases.operation_nightfall import get_operation_nightfall_case
import asyncio

async def main():
    print("[1] Testing Air-Gap socket monitor...")
    status = AirGapMonitor.check_network_isolation()
    print(f"    -> Air-Gapped: {status.is_airgapped}, Message: {status.verification_message}")

    print("[2] Loading Operation Nightfall sample case...")
    evidence = get_operation_nightfall_case()
    print(f"    -> Loaded {len(evidence)} evidence items:")
    for ev in evidence:
        print(f"       * {ev.id}: {ev.filename} ({ev.evidence_type.value}) - SHA: {ev.sha256_hash[:16]}...")

    print("[3] Running Forensic Cross-Examination...")
    report = await ForensicAnalyzer.analyze_case("CASE-TEST", "Operation Nightfall", evidence)
    print(f"    -> Summary: {report.summary}")
    print(f"    -> Contradictions Found: {report.contradiction_count}")
    for c in report.contradictions:
        print(f"       * [{c.severity}] {c.title}")
        print(f"         Source A: {c.source_a_quote[:50]}...")
        print(f"         Source B: {c.source_b_quote[:50]}...")
    print(f"    -> Timeline Events: {report.timeline_count}")
    print(f"    -> Entities Extracted: {report.entity_count}")
    print("\n[SUCCESS] Backend test completed cleanly!")

if __name__ == "__main__":
    asyncio.run(main())

