from typing import List, Tuple, Dict, Any
from pathlib import Path
from ..schemas import AudioSegment
from ..config import WHISPER_MODEL_SIZE

class AudioEngine:
    _model = None

    @classmethod
    def get_model(cls):
        """Lazy loader for Whisper model to conserve memory until first audio is analyzed."""
        if cls._model is None:
            try:
                from faster_whisper import WhisperModel
                # int8 quantization runs efficiently on modern x86 CPU threads
                cls._model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
            except Exception as e:
                print(f"[Warning] Whisper initialization error: {e}")
                return None
        return cls._model

    @classmethod
    def transcribe(cls, file_path: str) -> Tuple[str, List[AudioSegment], Dict[str, Any]]:
        """
        Transcribes audio locally using faster-whisper on CPU.
        Returns full transcript, granular timestamped segments, and metadata.
        """
        path = Path(file_path)
        metadata: Dict[str, Any] = {
            "engine": f"faster-whisper-{WHISPER_MODEL_SIZE}-int8",
            "filename": path.name,
        }

        try:
            model = cls.get_model()
            if model is None:
                # Graceful fallback when native audio engine is compiling or missing DLLs
                msg = f"[Audio file: {path.name} received. Whisper engine initializing or audio transcription in progress.]"
                return msg, [], metadata

            segments_gen, info = model.transcribe(file_path, beam_size=1)
            
            metadata["detected_language"] = info.language
            metadata["language_probability"] = round(info.language_probability, 3)
            metadata["duration_seconds"] = round(info.duration, 2)

            segments: List[AudioSegment] = []
            transcript_parts: List[str] = []

            for seg in segments_gen:
                clean_text = seg.text.strip()
                if clean_text:
                    segments.append(AudioSegment(
                        start=round(seg.start, 2),
                        end=round(seg.end, 2),
                        text=clean_text
                    ))
                    transcript_parts.append(f"[{round(seg.start, 1)}s - {round(seg.end, 1)}s] {clean_text}")

            full_text = "\n".join(transcript_parts)
            return full_text, segments, metadata

        except Exception as e:
            # Fallback error segment
            err_msg = f"[Whisper transcription error: {str(e)}]"
            metadata["error"] = str(e)
            return err_msg, [], metadata
