from app.core.services.document_service import DocumentService
import uuid
from utl.date_util import DateUtil
from utl.constantes import Constantes
from app.core.domain.manifiesto import Manifiesto
from app.core.repository.manifiesto_repository import ManifiestoRepository
from app.core.domain.guia_aerea import GuiaAerea
from app.core.services.manifiesto_service import ManifiestoService
from core.service.service_base import ServiceBase

class ManifiestoServiceImpl(ManifiestoService, ServiceBase):

    def __init__(self, manifiesto_repository: ManifiestoRepository, document_service: DocumentService):
        self.manifiesto_repository = manifiesto_repository
        self.document_service = document_service
    
    async def associate_guia(self, t: GuiaAerea):
      
        if not t.numero_vuelo or not t.fecha_vuelo:
            return 

        current_guia_db = await self.document_service.get(str(t.guia_aerea_id))
        manifiesto = await self.manifiesto_repository.find_by_vuelo_fecha(t.numero_vuelo, t.fecha_vuelo)

        if manifiesto:
            if current_guia_db.manifiesto_id == manifiesto.manifiesto_id:
                return 
            manifiesto.total_guias += 1
            if t.cantidad_piezas:
                manifiesto.total_bultos += t.cantidad_piezas
            if t.peso_bruto:
                manifiesto.peso_bruto_total += t.peso_bruto
            if t.volumen:
                manifiesto.volumen_total += t.volumen
            
            self._validate_and_update_status(manifiesto)
            await self.manifiesto_repository.save(manifiesto)
            
        else: 
            manifiesto = Manifiesto(
                manifiesto_id = uuid.uuid4(),
                numero_vuelo = t.numero_vuelo,
                fecha_vuelo = t.fecha_vuelo,
                aerolinea_codigo = t.aerolinea_codigo,
                origen_codigo = t.origen_codigo,
                destino_codigo = t.destino_codigo,
                total_guias = 1,
                total_bultos = t.cantidad_piezas or 0,
                peso_bruto_total = t.peso_bruto or 0.00,
                volumen_total = t.volumen or 0.000,
                estado_codigo = Constantes.EstadoManifiesto.BORRADOR,
                habilitado = Constantes.HABILITADO, 
                creado = DateUtil.get_current_local_datetime(),
                creado_por = self.session.full_name if hasattr(self, 'session') and self.session else Constantes.SYSTEM_USER
            )
            self._validate_and_update_status(manifiesto)
            await self.manifiesto_repository.save(manifiesto)

        await self.document_service.setManifiesto(manifiesto.manifiesto_id, t.guia_aerea_id)
        
        # Re-validate after adding (in case of updates)
        # Note: If it was an update block above, we missed saving the validation.
        # Let's fix the UPDATE block too.

    def _validate_and_update_status(self, m: Manifiesto):
        import json
        errors = []
        if (m.peso_bruto_total or 0) <= 0:
            errors.append("Peso total es 0.")
        if (m.total_bultos or 0) <= 0:
            errors.append("Total bultos es 0.")
        if not m.aerolinea_codigo:
            errors.append("Falta código de aerolínea.")
        
        m.es_valido = len(errors) == 0
        m.errores_validacion = json.dumps(errors) if errors else None
        