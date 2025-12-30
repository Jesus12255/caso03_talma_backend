from abc import abstractmethod

from uuid import UUID
from app.core.domain.interviniente import Interviniente
from app.core.repository.interviniente_repository import IntervinienteRepository
from app.core.services.interviniente_service import IntervinienteService
from config.mapper import Mapper
from core.service.service_base import ServiceBase
from dto.interviniente_dtos import IntervinienteRequest

from utl.date_util import DateUtil

class IntervinienteServiceImpl(IntervinienteService, ServiceBase):

    def __init__(self, interviniente_repository: IntervinienteRepository):
        self.interviniente_repository = interviniente_repository
    
    async def save(self, request: IntervinienteRequest) -> UUID:
        # Check for duplicate
        if request.numeroDocumento and request.tipoCodigo:
            existing = await self.interviniente_repository.find_by_documento_tipo(
                request.numeroDocumento, 
                request.tipoCodigo
            )
            if existing:
                updated = False
                # Campos a verificar: {campo_request: campo_entity}
                fields_map = {
                    "direccion": "direccion",
                    "ciudad": "ciudad",
                    "telefono": "telefono",
                    "paisCodigo": "pais_codigo",
                    "nombre": "nombre"
                }

                for req_field, entity_field in fields_map.items():
                    new_val = getattr(request, req_field)
                    old_val = getattr(existing, entity_field)
                    
                    # Solo actualizamos si el nuevo valor no es vacío y es diferente al anterior
                    if new_val and new_val != old_val:
                        setattr(existing, entity_field, new_val)
                        updated = True

                if updated:
                    existing.modificado = DateUtil.get_current_local_datetime()
                    # Usar SYSTEM_USER si no hay sesión (ej. background), o nombre de sesión si existe
                    user_name = self.session.full_name if hasattr(self, 'session') and self.session and self.session.full_name else "SYSTEM"
                    existing.modificado_por = user_name
                    
                    await self.interviniente_repository.update(existing.interviniente_id, existing)

                return existing.interviniente_id

        interviniente = Mapper.to_entity(request, Interviniente)
        await self.interviniente_repository.save(interviniente)
        return interviniente.interviniente_id