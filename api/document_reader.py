from __future__ import annotations

from io import BytesIO
import importlib

import pdfplumber
from PIL import Image, UnidentifiedImageError

try:
    import pytesseract
except Exception:  # pragma: no cover
    pytesseract = None


class DocumentReaderService:
    def __init__(self) -> None:
        self._ocr_engine = None
        self._ocr_available = None

    def extract_text(self, uploaded_file) -> str:
        if uploaded_file is None:
            return ""

        file_name = str(getattr(uploaded_file, "name", "")).lower()
        content_type = str(getattr(uploaded_file, "content_type", "")).lower()

        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        raw_bytes = uploaded_file.read()
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

        if not raw_bytes:
            return ""

        if "pdf" in content_type or file_name.endswith(".pdf"):
            return self._extract_pdf_text(raw_bytes)

        return self._extract_image_text(raw_bytes)

    def _extract_pdf_text(self, raw_bytes: bytes) -> str:
        pages: list[str] = []
        with pdfplumber.open(BytesIO(raw_bytes)) as pdf:
            for page in pdf.pages:
                text = self._clean_text(page.extract_text() or "")
                if text:
                    pages.append(text)
        return "\n".join(pages).strip()

    def _extract_image_text(self, raw_bytes: bytes) -> str:
        try:
            image = Image.open(BytesIO(raw_bytes)).convert("RGB")
        except UnidentifiedImageError:
            return ""

        rapid_text = self._extract_with_rapidocr(image)
        if rapid_text:
            return rapid_text

        return self._extract_with_tesseract(image)

    def _extract_with_rapidocr(self, image: Image.Image) -> str:
        if self._ocr_available is False:
            return ""

        try:
            np = importlib.import_module("numpy")
            rapidocr_module = importlib.import_module("rapidocr_onnxruntime")
        except Exception:
            self._ocr_available = False
            return ""

        if self._ocr_engine is None:
            try:
                self._ocr_engine = rapidocr_module.RapidOCR()
                self._ocr_available = True
            except Exception:
                self._ocr_available = False
                return ""

        try:
            result, _ = self._ocr_engine(np.array(image))
        except Exception:
            return ""

        if not result:
            return ""

        parts = []
        for item in result:
            if len(item) >= 2 and item[1]:
                parts.append(str(item[1]))
        return self._clean_text(" ".join(parts))

    def _extract_with_tesseract(self, image: Image.Image) -> str:
        if pytesseract is None:
            return ""
        try:
            return self._clean_text(pytesseract.image_to_string(image))
        except Exception:
            return ""

    def build_attachment_context(self, uploaded_file, extracted_text: str) -> dict[str, object]:
        if uploaded_file is None:
            return {}

        cleaned_text = self._clean_text(extracted_text)
        preview = cleaned_text[:500]
        if len(cleaned_text) > 500:
            preview += "..."

        return {
            "filename": getattr(uploaded_file, "name", ""),
            "content_type": getattr(uploaded_file, "content_type", ""),
            "extracted_text": cleaned_text,
            "preview": preview,
            "has_text": bool(cleaned_text),
        }

    def _clean_text(self, text: str) -> str:
        return " ".join(str(text or "").split())


document_reader_service = DocumentReaderService()
