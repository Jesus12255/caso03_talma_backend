import base64
import fitz  # PyMuPDF
import io
from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile
import zipfile
from core.exceptions import AppBaseException
from utl.constantes import Constantes

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

            return False

    @staticmethod
    async def validate_file(file: UploadFile):
        VALID_FORMATS = Constantes.VALID_FILE_FORMATS

        ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        # 0. Validacion de tamanio
        if file.size > Constantes.MAX_FILE_SIZE:
             raise AppBaseException(message=f"El archivo '{file.filename}' excede el tamaño máximo permitido ({Constantes.MAX_FILE_SIZE_TEXT}).")

        # 1. Validacion rapida: Extension y MIME
        if ext not in VALID_FORMATS:
            raise AppBaseException(message=f"El archivo '{file.filename}' tiene una extensión no permitida.")
        
        if file.content_type not in VALID_FORMATS[ext]['mime']:
             raise AppBaseException(message=f"El archivo '{file.filename}' no coincide con su extensión.")

        # Leer contenido
        content = await file.read()
        await file.seek(0) # Reset cursor

        # 2. Validacion eficiente: Magic Numbers
        if not content.startswith(VALID_FORMATS[ext]['magic']):
            raise AppBaseException(message=f"El archivo '{file.filename}' no es un {ext.upper().replace('.', '')} válido (Firma incorrecta).")

        # 3. Validacion profunda: Integridad y Contraseña
        try:
            if ext == '.pdf':
                try:
                    with fitz.open(stream=content, filetype="pdf") as doc:
                        if doc.needs_pass:
                            raise AppBaseException(message=f"El archivo '{file.filename}' está protegido con contraseña.")
                except fitz.FileDataError:
                     raise AppBaseException(message=f"El archivo '{file.filename}' está dañado o no es un PDF válido.")
            
            elif ext in ['.jpg', '.jpeg', '.png']:
                try:
                    img = Image.open(io.BytesIO(content))
                    img.verify() 
                except Exception:
                    raise AppBaseException(message=f"El archivo '{file.filename}' es una imagen dañada.")
                    
            elif ext in ['.docx', '.xlsx']:
                if not zipfile.is_zipfile(io.BytesIO(content)):
                    raise AppBaseException(message=f"El archivo '{file.filename}' está dañado.")
                    
        except AppBaseException:
            raise
        except Exception as e:
            # logger no esta disponible aqui directamente, podriamos inyectarlo o simplemente lanzar la excepcion
            raise AppBaseException(message=f"Error al validar integridad de '{file.filename}'.")
