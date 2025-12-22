import base64
import fitz  # PyMuPDF
import io
from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile

class FileUtil:

    @staticmethod
    def to_base64(data: bytes) -> str:
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def is_valid_pdf(data: bytes) -> bool:
        try:
            # Intentar abrir el PDF con PyMuPDF desde el stream de bytes
            doc = fitz.open(stream=data, filetype="pdf")
            if doc.page_count > 0:
                doc.close()
                return True
            doc.close()
            return False
        except Exception:
            return False

    @staticmethod
    def is_valid_image(data: bytes) -> bool:
        try:
            img = Image.open(io.BytesIO(data))
            img.verify() 
            return True
        except (UnidentifiedImageError, IOError):
            return False

