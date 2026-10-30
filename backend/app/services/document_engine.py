from pathlib import Path
from typing import Dict, Any, Tuple

class DocumentEngine:
    @staticmethod
    def extract_text_from_file(file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extracts clean text and structural metadata from PDF or plain text files.
        Uses pure-Python pypdf with fallback for zero-dependency reliability.
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        metadata: Dict[str, Any] = {
            "extension": ext,
            "filename": path.name,
            "pages": 1
        }

        if ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                metadata["pages"] = len(reader.pages)
                
                text_pages = []
                for idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text_pages.append(f"--- [Page {idx + 1}] ---\n{page_text}")
                
                full_text = "\n\n".join(text_pages) if text_pages else "[Empty or scanned PDF - No text layer]"
                return full_text, metadata
            except Exception as e:
                # Try fallback PyMuPDF if installed
                try:
                    import fitz
                    doc = fitz.open(file_path)
                    metadata["pages"] = len(doc)
                    text_pages = [f"--- [Page {i+1}] ---\n{p.get_text()}" for i, p in enumerate(doc) if p.get_text().strip()]
                    doc.close()
                    return "\n\n".join(text_pages), metadata
                except Exception:
                    return f"[Error parsing PDF: {str(e)}]", metadata

        elif ext in [".txt", ".log", ".csv", ".json", ".md"]:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
                return text, metadata
            except Exception as e:
                return f"[Error reading text file: {str(e)}]", metadata

        else:
            return f"[Unsupported document format: {ext}]", metadata
