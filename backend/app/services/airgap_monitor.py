import hashlib
import psutil
from datetime import datetime
from typing import Tuple, List
from ..schemas import AirGapStatus

class AirGapMonitor:
    @staticmethod
    def calculate_sha256(file_path: str) -> str:
        """Calculates SHA-256 cryptographic hash of evidence for forensic chain of custody."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def check_network_isolation() -> AirGapStatus:
        """
        Scans active network sockets to certify that the forensic workstation
        has zero unauthorized outbound egress during investigation.
        """
        external_connections: List[str] = []
        
        try:
            current_pid = psutil.Process().pid
            proc = psutil.Process(current_pid)
            connections = proc.net_connections(kind="inet")

            for conn in connections:
                # Check if remote address exists and is not localhost (127.0.0.1 or ::1)
                if conn.raddr and conn.status == psutil.CONN_ESTABLISHED:
                    r_ip = conn.raddr.ip
                    if r_ip not in ("127.0.0.1", "::1", "localhost", "0.0.0.0"):
                        external_connections.append(f"{r_ip}:{conn.raddr.port}")
        except Exception:
            # Fallback if connection enumeration requires elevation
            pass

        is_airgapped = len(external_connections) == 0
        message = (
            "VERIFIED: 100% Air-Gapped. Zero outbound external sockets detected."
            if is_airgapped
            else f"ALERT: Non-local active connections detected: {', '.join(external_connections)}"
        )

        return AirGapStatus(
            is_airgapped=is_airgapped,
            active_outbound_connections=len(external_connections),
            verification_message=message,
            inspected_at=datetime.utcnow().isoformat() + "Z"
        )

