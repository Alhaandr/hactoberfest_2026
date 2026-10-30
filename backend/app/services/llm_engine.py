import json
import socket
from urllib.parse import urlparse
import httpx
from typing import Dict, Any, Optional
from ..config import OLLAMA_BASE_URL, DEFAULT_MODEL

class LLMEngine:
    @staticmethod
    def _is_service_listening() -> bool:
        """Fast low-level socket probe to verify port is actively open without Proactor hangs."""
        try:
            parsed = urlparse(OLLAMA_BASE_URL)
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or 11434
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                return s.connect_ex((host, port)) == 0
        except Exception:
            return False

    @staticmethod
    async def is_ollama_available() -> bool:
        """Checks if local Ollama daemon is responsive."""
        if not LLMEngine._is_service_listening():
            return False
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    @staticmethod
    async def list_available_models() -> list:
        """Returns list of models installed in local Ollama instance."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    @classmethod
    async def generate_json(cls, prompt: str, system_prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends query to local Ollama LLM requesting strict JSON formatted response.
        Falls back cleanly if Ollama is unreachable.
        """
        target_model = model or DEFAULT_MODEL

        # Fast pre-check to prevent long connection timeouts when Ollama daemon is off
        if not await cls.is_ollama_available():
            return {"error": "Local Ollama daemon is unreachable."}

        payload = {
            "model": target_model,
            "prompt": prompt,
            "system": system_prompt + "\nIMPORTANT: You must reply ONLY with valid JSON conforming to the requested schema. Do not include markdown codeblocks or conversational text.",
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for strict factual extraction
                "top_p": 0.9,
                "num_predict": 2048
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
                if res.status_code == 200:
                    response_json = res.json()
                    response_text = response_json.get("response", "{}")
                    return json.loads(response_text)
                else:
                    return {"error": f"Ollama HTTP error {res.status_code}: {res.text}"}
        except json.JSONDecodeError:
            # Fallback for minor formatting discrepancies
            return {"error": "Failed to parse model output as valid JSON"}
        except Exception as e:
            return {"error": f"LLM Inference connection error: {str(e)}"}

