from core.facade.facade_base import FacadeBase
import asyncio
import base64
import logging
from typing import List, TypedDict, AsyncGenerator, Tuple, Optional
from pathlib import Path
from fastapi import UploadFile
from uuid import UUID

from app.core.facade.document_facade import DocumentFacade
from app.core.services.analyze_service import AnalyzeService
from app.core.services.document_service import DocumentService
from app.integration.extraction_engine import ExtractionEngine
from app.integration.service.storage_service import StorageService
from core.tasks.document_tasks import process_document_validations
from dto.guia_aerea_dtos import GuiaAereaRequest
from utl.constantes import Constantes
from utl.file_parser import FileParser
from utl.file_util import FileUtil
from utl.generic_util import GenericUtil

logger = logging.getLogger(__name__)



class FileData(TypedDict):
    filename: str
    content: bytes
Task = Tuple[asyncio.Task, str, bytes]



class AnalyzeServiceImpl(AnalyzeService, FacadeBase):

    def __init__(self, extraction_engine: ExtractionEngine, document_service: DocumentService, document_facade: DocumentFacade, storage_service: StorageService ):
        self.extraction_engine = extraction_engine
        self.document_service = document_service
        self.document_facade = document_facade
        self.storage_service = storage_service



    async def process_stream(self, files_data: List[FileData]) -> AsyncGenerator[dict, None]:

        if not files_data:
            yield self._error("No se encontraron documentos válidos")
            return

        yield self._thinking("Iniciando escaneo de superficie digital...")
        tasks: List[Task] = []
        page_index = 1
        for file in files_data:
            filename, content = file.values()

            yield self._thinking(f"Vectorizando contenido de {filename}...")
            task_info = await self._build_task(content, filename, page_index)

            if not task_info:
                yield self._warning(f"No se pudo leer el archivo {filename}")
                continue

            task, pages = task_info
            tasks.append((task, filename, content))
            page_index += pages

            yield self._thinking(f"Documento {filename} preparado para análisis.")

        if not tasks:
            yield self._warning("No se pudo preparar ningún documento para análisis")
            return

       
        yield self._thinking("Iniciando extracción neuronal paralela...")
        documents = await self._execute_tasks(tasks)

     
        for doc in documents:
            if not doc.get("isValid", True):
                 yield self._warning(f"El archivo {doc.get('fileName')} no es una guía aérea válida.")

        yield {"type": "response", "documents": documents}

      
        async for event in self._persist_documents(documents):
            yield event

        yield self._thinking("Proceso finalizado con éxito.")

    async def read_and_validate(
        self,
        files: List[UploadFile]
    ) -> List[FileData]:
        return [
            {
                "filename": file.filename,
                "content": await self._validate_and_read(file)
            }
            for file in files
        ]


    async def _upload_safe(self, filename: str, content: bytes) -> Optional[str]:
        try:
            return await self.storage_service.upload_file(
                filename,
                content,
                self._detect_mime(filename)
            )
        except Exception as exc:
            logger.warning("Upload failed for %s: %s", filename, exc)
            return None


    async def _build_task(self, content: bytes, filename: str, start_index: int) -> Optional[Tuple[asyncio.Task, int]]:
        if FileUtil.is_valid_docx(content) or FileUtil.is_valid_xlsx(content):
            return await self._build_text_task(content, filename, start_index)
        return self._build_binary_task(content, filename, start_index)

    async def _build_text_task(self, content: bytes, filename: str, start_index: int) -> Optional[Tuple[asyncio.Task, int]]:
        loop = asyncio.get_running_loop()
        _, text = await loop.run_in_executor(
            None,
            FileParser.parse,
            content,
            filename
        )

        if not text:
            return None

        return (
            self.extraction_engine.extract_single_document(
                base64.b64encode(text.encode()).decode(),
                "text/plain",
                1,
                start_index
            ),
            1
        )

    def _build_binary_task( self, content: bytes, filename: str, start_index: int) -> Optional[Tuple[asyncio.Task, int]]:
        images, _ = FileParser.parse(content, filename)
        if not images:
            return None
        return (
            self.extraction_engine.extract_single_document(
                images[0],
                "image/jpeg",
                len(images),
                start_index
            ),
            len(images)
        )



    async def _execute_tasks(self, tasks: List[Task]) -> List[dict]:

        async def safe(task: asyncio.Task, fname: str, fcontent: bytes):
            try:
                res = await task
                return res, fname, fcontent
            except Exception as exc:
                logger.exception("Error procesando %s", fname)
                return [{"error": str(exc)}], fname, fcontent

        coroutines = [safe(task, fname, content) for task, fname, content in tasks]
        documents: List[dict] = []

        for future in asyncio.as_completed(coroutines):
            results, fname, content = await future

            if self._is_invalid(results):
                documents.append(self._invalid_document(fname, results[0]))
                continue
            path_file = Path(fname)
            name = path_file.stem
            extension = path_file.suffix
            path = f"{Constantes.RutasArchivos.GUIAS_AEREAS}{name}{GenericUtil.build_code_8_unic()}{extension}"
            
            public_url = await self._upload_safe(path, content)
    
            documents.extend(self._normalize_results(results, fname, public_url))

        return documents



    def _normalize_results(self, results: list, filename: str, url: Optional[str] = None) -> List[dict]:
        return [
            {
                **{
                    k: v for k, v in r.get("fields", r).items()
                    if k not in {"document_index", "document_name", "fileName", "error"}
                },
                "fileName": filename,
                "url": url,
                "isValid": True
            }
            for r in results
        ]



    async def _persist_documents(
        self,
        documents: List[dict]
    ) -> AsyncGenerator[dict, None]:

        seen_numeros = set()

        for doc in filter(lambda d: d.get("isValid", True), documents):
            fname = doc.get("fileName", "Documento")
            yield self._thinking(f"Sincronizando {fname} en base de datos...")

            guia = self._build_guia(doc)
            if not guia:
                continue
            guia.usuarioId = UUID(self.session.user_id) if self.session.user_id else None
            
            # Batch deduplication
            if guia.numero and guia.numero in seen_numeros:
                yield self._warning(f"Omitiendo duplicado en lote: {guia.numero}")
                continue
            
            if guia.numero:
                seen_numeros.add(guia.numero)

            self.document_facade.validar_campos_requeridos_guia_aerea(guia)
            await self.document_service.saveOrUpdate(guia)

            if guia.guiaAereaId:
                process_document_validations.delay(guia.model_dump_json())

        yield self._thinking("Procesamiento en segundo plano iniciado.")



    async def _validate_and_read(self, file: UploadFile) -> bytes:
        await FileUtil.validate_file(file)
        return await file.read()

    def _detect_mime(self, filename: str) -> str:
        return "application/pdf" if filename.lower().endswith(".pdf") else "application/octet-stream"

    def _build_guia(self, doc: dict) -> Optional[GuiaAereaRequest]:
        try:
            doc.setdefault("totalFlete", 0.0)
            
            # Fix types for Pydantic validation
            if "confianzas" in doc and isinstance(doc["confianzas"], list):
                for c in doc["confianzas"]:
                    if "valorExtraido" in c and c["valorExtraido"] is not None:
                         c["valorExtraido"] = str(c["valorExtraido"])
            
            return GuiaAereaRequest(**doc)
        except Exception as exc:
            logger.error("Error building guia: %s", exc)
            return None

    def _is_invalid(self, results: list) -> bool:
        return bool(results and isinstance(results, list) and results[0].get("error"))

    def _invalid_document(self, filename: str, error: dict) -> dict:
        return {
            "fileName": filename,
            "error": error.get("error"),
            "message": error.get("mensaje", "Error desconocido"),
            "isValid": False
        }


    def _thinking(self, message: str) -> dict:
        return {"type": "thinking", "message": message}

    def _warning(self, message: str) -> dict:
        return {"type": "warning", "message": message}

    def _error(self, message: str) -> dict:
        return {"type": "error", "message": message}
