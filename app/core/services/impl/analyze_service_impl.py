import asyncio
import base64
import logging
from typing import List, TypedDict

from fastapi import UploadFile

from app.core.facade.document_facade import DocumentFacade
from app.core.services.analyze_service import AnalyzeService
from app.core.services.document_service import DocumentService
from app.integration.extraction_engine import ExtractionEngine
from core.exceptions import AppBaseException
from core.tasks.document_tasks import process_document_validations
from dto.universal_dto import BaseOperacionResponse
from utl.file_parser import FileParser
from utl.file_util import FileUtil
from dto.guia_aerea_dtos import GuiaAereaRequest

logger = logging.getLogger(__name__)


class FileData(TypedDict):
    filename: str
    content: bytes


class AnalyzeServiceImpl(AnalyzeService):

    def __init__(self, extraction_engine: ExtractionEngine, document_service: DocumentService, document_facade: DocumentFacade):
        self.extraction_engine = extraction_engine
        self.document_service = document_service
        self.document_facade = document_facade

    async def process_stream(self, files_data: List[FileData]):

        if not files_data:
            yield {"type": "error", "message": "No se encontraron documentos válidos"}
            return

        yield {"type": "thinking", "message": "Iniciando escaneo de superficie digital..."}

        # 1. Prepare Tasks with Granular Feedback
        tasks = []
        page_index = 1
        
        for idx, f in enumerate(files_data, start=1):
            filename = f["filename"]
            yield {"type": "thinking", "message": f"Vectorizando contenido de {filename}..."}
            
            content = f["content"]
            task_info = await self._build_task(content, filename, page_index)
            
            if not task_info:
                yield {"type": "warning", "message": f"No se pudo leer el archivo {filename}"}
                continue

            task, pages = task_info
            tasks.append((task, filename))
            page_index += pages
            
            yield {"type": "thinking", "message": f"Documento {filename} preparado para análisis."}

        # 2. Execute Analysis with Real-time Progress
        yield {"type": "thinking", "message": "Iniciando extracción neuronal paralela..."}
        
        documents = []
        async for event in self._execute_tasks_stream(tasks):
            if event["type"] == "thinking":
                 yield event
            elif event["type"] == "result":
                 documents.extend(event["data"])
        
        # Notify about invalid documents
        for doc in documents:
            if doc.get("error") == "DOCUMENTO_INVALIDO":
                 yield {"type": "warning", "message": f"El archivo {doc.get('fileName')} no es una guía aérea válida."}

        yield {"type": "response", "documents": documents}

        # 3. Save
        async for event in self._auto_save(documents):
            yield event

        yield {"type": "thinking", "message": "Proceso finalizado con éxito."}


    async def read_and_validate(self, files: List[UploadFile]) -> List[FileData]:
        result: List[FileData] = []

        for file in files:
            await FileUtil.validate_file(file)
            content = await file.read()
            result.append({
                "filename": file.filename,
                "content": content
            })
        return result

    async def _prepare_tasks(self, files: List[FileData]):
        # DEPRECATED: Logic moved to process_stream for better feedback control
        pass

    async def _build_task(self, content: bytes, filename: str, start_index: int):
        if FileUtil.is_valid_xlsx(content) or FileUtil.is_valid_docx(content):
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

        binary = self._prepare_binary_document(content, filename)
        if not binary:
            return None

        return (
            self.extraction_engine.extract_single_document(
                binary["base64"],
                binary["mime_type"],
                binary["page_count"],
                start_index
            ),
            binary["page_count"]
        )

    def _prepare_binary_document(self, content: bytes, filename: str):
        images, _ = FileParser.parse(content, filename)

        if not images:
            return None

        return {
            "base64": images[0],
            "mime_type": "image/jpeg",
            "page_count": len(images)
        }

    async def _execute_tasks_stream(self, tasks):
        
        async def safe(task, filename):
            try:
                result = await task
                return result, filename
            except Exception as e:
                logger.exception("Error procesando %s", filename)
                return [{"error": str(e)}], filename

        running = [safe(task, fname) for task, fname in tasks]
        
        if not running:
            return

        for future in asyncio.as_completed(running):
            results, fname = await future
            
            # Yield progress for this file
            yield {"type": "thinking", "message": f"Entidades extraídas de {fname}..."}
            
            # Check if it is an invalid document error (Rule 9)
            if results and isinstance(results, list) and results[0].get("error"):
                 yield {"type": "result", "data": [{
                     "fileName": fname,
                     "error": results[0].get("error"),
                     "message": results[0].get("mensaje", "Error desconocido"),
                     "isValid": False
                 }]}
                 continue

            yield {"type": "thinking", "message": f"Validando confianza de datos para {fname}..."}
            normalized_docs = self._normalize_results(results, fname)
            yield {"type": "result", "data": normalized_docs}
            
    # keep _execute_tasks for backward compatibility if needed, but we rely on stream now
    async def _execute_tasks(self, tasks):
        documents = []
        async for event in self._execute_tasks_stream(tasks):
            if event["type"] == "result":
                documents.extend(event["data"])
        return documents

    def _normalize_results(self, results, filename):
        normalized = []
        for r in results:
            doc = {}
            
            source_data = r.get("fields", r)
            
            for k, v in source_data.items():
                if k not in ["document_index", "document_name", "fileName", "error"]:
                    doc[k] = v
            
            doc["fileName"] = filename
            doc["isValid"] = True
            normalized.append(doc)
        return normalized

    async def _auto_save(self, documents):

        try:
            total = len([d for d in documents if d.get("isValid", True)])
            current = 0
            
            for tt in documents:
                # Skip invalid documents
                if not tt.get("isValid", True):
                    continue
                
                fname = tt.get("fileName", "Documento")
                yield {"type": "thinking", "message": f"Sincronizando {fname} en base de datos..."}

                guia = self._build_guia(tt)
                if not guia:
                    continue
                obj_req = GuiaAereaRequest.model_validate(guia)
                self.document_facade.validar_campos_requeridos_guia_aerea(obj_req)
                await self.document_service.saveOrUpdate(obj_req)
                if obj_req.guiaAereaId:
                    process_document_validations.delay(obj_req.model_dump_json())
                
                current += 1
                
            yield {"type": "thinking", "message": "Procesamiento en segundo plano iniciado para todos los documentos."}
        
        except Exception as e:
            logger.error(f"Error al guardar documentos: {e}")
            yield {"type": "warning", "message": f"Error al guardar datos: {e}"}
            # Don't raise, so other docs can be processed or stream finishes gracefully
            # raise AppBaseException(message=f"Error al procesar la solicitud: {e}")



    def _build_guia(self, doc: dict):
        try:
            if doc.get("totalFlete") is None:
                doc["totalFlete"] = 0.0
            return GuiaAereaRequest(**doc)
        except Exception as e:
            logger.error(f"Error building guia object: {e}")
            return None
