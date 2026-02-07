from dto.trama_dtos import ManifiestoResponse
from dto.trama_dtos import ManifiestoFiltroRequest
from dto.trama_dtos import TramaFiltroRequest
from core.exceptions import AppBaseException
from app.core.domain.guia_aerea_data_grid import GuiaAereaDataGrid
from abc import abstractmethod
from abc import ABC
from typing import List
from io import BytesIO
from app.core.domain.guia_aerea import GuiaAerea

class TramaService(ABC):
    
    @abstractmethod
    async def find(self, request: TramaFiltroRequest) -> tuple[List[GuiaAereaDataGrid], int]:
        pass

    @abstractmethod
    async def findTramas(self, request: ManifiestoFiltroRequest) -> tuple[List[ManifiestoResponse], int]:
        pass

    @abstractmethod
    async def get_records_by_manifiesto_ids(self, ids: List[str]) -> List[GuiaAereaDataGrid]:
        pass

    @abstractmethod
    async def get_data_grid_records_by_ids(self, ids: List[str]) -> List[GuiaAereaDataGrid]:
        pass

    @abstractmethod
    async def get_data_grid_records_by_manifiesto_id(self, manifiesto_id: str) -> List[GuiaAereaDataGrid]:
        pass

    async def validate_batch(self, guias: List[GuiaAerea]) -> dict:

        if not guias:
            raise AppBaseException("No se han seleccionado guías.")

        vuelos = set(g.numero_vuelo for g in guias if g.numero_vuelo)
        if len(vuelos) > 1:
            warnings.append(f"Se han seleccionado guías de {len(vuelos)} vuelos distintos: {', '.join(vuelos)}. ¿Seguro que desea mezclarlos?")
            
        # 2. Validar consistencia de Moneda (A veces aduana pide todo en USD)
        monedas = set(g.moneda_codigo for g in guias if g.moneda_codigo)
        if len(monedas) > 1:
            warnings.append(f"Mezcla de monedas detectada: {', '.join(monedas)}.")

        # 3. Validar Pesos
        peso_total = sum(g.peso_bruto or 0 for g in guias)
        if peso_total <= 0:
            errors.append("El peso total del lote es 0. Verifique los pesos individuales.")

        status = "OK"
        if errors:
            status = "ERROR"
        elif warnings:
            status = "WARNING"
            
        return {
            "status": status,
            "messages": errors + warnings,
            "resumen": {
                "total_guias": len(guias),
                "peso_total": float(peso_total),
                "piezas_total": sum(g.cantidad_piezas or 0 for g in guias)
            }
        }

    def generate_flat_file_content(self, guias: List[GuiaAerea]) -> str:
        """
        Genera el contenido del archivo plano (TXT) siguiendo formato estándar (Simulado por ahora).
        Format: FWB/ver/ROUTING/CONSIGNEE/SHIPPER...
        """
        lines = []
        # Header (Simulated Flight Header)
        vuelo = guias[0].numero_vuelo if guias else "UNKNOWN"
        lines.append(f"FFM/8/{vuelo}") 
        
        for guia in guias:
            # Ejemplo de línea tipo FWB (Simplificado)
            # FWB/NumGuia/OrigenDestino/Piezas/Peso/Volumen
            line = f"FWB/14/{guia.numero}/{guia.origen_codigo}{guia.destino_codigo}/{guia.cantidad_piezas}/{guia.peso_bruto}/{guia.volumen or 0.0}"
            lines.append(line)
            
        return "\n".join(lines)

    @abstractmethod
    async def generate_manifest_pdf(self, guias: List[GuiaAereaDataGrid]) -> BytesIO:
        """
        Genera un PDF simple usando reportlab.
        """
        pass

    @abstractmethod
    async def generate_manifest_xml(self, guias: List[GuiaAerea]) -> str:
        """
        Genera el contenido del manifiesto en formato XML (SUNAT OMA v3.7).
        """
        pass
