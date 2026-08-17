from io import BytesIO
from typing import BinaryIO, Union

from pypdf import PdfReader


PDFSource = Union[bytes, bytearray, BinaryIO]


class PDFProcessor:
    """Extract text from PDFs without imposing an artificial character limit."""

    def extract_text(self, file_source: PDFSource) -> dict:
        if not file_source:
            raise ValueError("The uploaded PDF is empty.")

        try:
            if isinstance(file_source, (bytes, bytearray)):
                stream = BytesIO(file_source)
            else:
                stream = file_source
                try:
                    stream.seek(0)
                except Exception:
                    pass

            reader = PdfReader(stream)
        except Exception as error:
            raise ValueError(f"Invalid PDF file: {error}") from error

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""

            text = text.strip()

            if text:
                extracted_pages.append({
                    "page": page_number,
                    "text": text,
                })

        if not extracted_pages:
            raise ValueError(
                "No readable text was found in the PDF. "
                "If this is a scanned/image-only PDF, OCR is required."
            )

        text = "\n\n".join(
            page["text"] for page in extracted_pages
        )

        return {
            "success": True,
            "pages": len(reader.pages),
            "text_pages": len(extracted_pages),
            "characters": len(text),
            "text": text,
            "page_text": extracted_pages,
        }
