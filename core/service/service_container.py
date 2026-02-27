from app.core.services.impl.manifiesto_service_impl import ManifiestoServiceImpl
from app.core.services.impl.document_service_impl import DocumentServiceImpl
from app.core.services.impl.confianza_extraccion_service_impl import ConfianzaExtraccionServiceImpl
from app.core.services.impl.interviniente_service_impl import IntervinienteServiceImpl
from app.core.repository.impl.interviniente_repository_impl import IntervinienteRepositoryImpl
from app.core.repository.impl.guia_aerea_filtro_repository_impl import GuiaAereaFiltroRepositoryImpl
from app.core.repository.impl.document_repository_impl import DocumentRepositoryImpl
from app.core.services.impl.guia_aerea_interviniente_service_impl import GuiaAereaIntervinienteServiceImpl
from app.core.repository.impl.confianza_extraccion_repository_impl import ConfianzaExtraccionRepositoryImpl
from app.core.repository.impl.guia_aerea_interviniente_repository_impl import GuiaAereaIntervinienteRepositoryImpl
from app.core.services.impl.notificacion_service_impl import NotificacionServiceImpl
from app.core.repository.impl.notificacion_repository_impl import NotificacionRepositoryImpl
from app.core.repository.impl.manifiesto_repository_impl import ManifiestoRepositoryImpl
from app.core.services.impl.audit_service_impl import AuditServiceImpl
from app.core.repository.impl.audit_filtro_repository_impl import AuditFiltroRepositoryImpl
from app.core.repository.impl.audit_repository_impl import AuditRepositoryImpl
from app.core.repository.impl.perfil_riesgo_repository_impl import PerfilRiesgoRepositoryImpl
from app.configuration.repository.impl.catalogo_repository_impl import CatalogoRepositoryImpl
from app.core.services.impl.irregularidad_service_impl import IrregularidadServiceImpl
from app.integration.service.impl.embedding_service_impl import EmbeddingServiceImpl


class ServiceContainer:
    def __init__(self, db):
        self.auditoria_repository = AuditRepositoryImpl(db)
        self.auditoria_filtro_repository = AuditFiltroRepositoryImpl(db)
        self.auditoria_service = AuditServiceImpl(self.auditoria_repository, self.auditoria_filtro_repository)
            
        self.manifiesto_repository = ManifiestoRepositoryImpl(db)
        self.notificacion_repository = NotificacionRepositoryImpl(db)
        self.notificacion_service = NotificacionServiceImpl(self.notificacion_repository)
            
        self.guia_aerea_interviniente_repository = GuiaAereaIntervinienteRepositoryImpl(db)
        self.confianza_extraccion_repository = ConfianzaExtraccionRepositoryImpl(db)
        self.guia_aerea_interviniente_service = GuiaAereaIntervinienteServiceImpl(self.guia_aerea_interviniente_repository, self.confianza_extraccion_repository)
            
        self.guia_aerea_repository = DocumentRepositoryImpl(db)
        self.guia_aerea_filtro_repository = GuiaAereaFiltroRepositoryImpl(db)
        self.interviniente_repository = IntervinienteRepositoryImpl(db)
        self.interviniente_service = IntervinienteServiceImpl(self.interviniente_repository)
        self.conf_service = ConfianzaExtraccionServiceImpl(self.confianza_extraccion_repository)

        self.perfil_riesgo_repository = PerfilRiesgoRepositoryImpl(db)
        self.catalogo_repository = CatalogoRepositoryImpl(db)
        self.embedding_service = EmbeddingServiceImpl()
        
        self.irregularidad_service = IrregularidadServiceImpl(
            self.perfil_riesgo_repository,
            self.notificacion_repository,
            self.notificacion_service,
            self.guia_aerea_repository,
            self.guia_aerea_interviniente_service,
            self.embedding_service,
            self.auditoria_service
        )

        self.guia_aerea_service = DocumentServiceImpl(self.guia_aerea_repository, self.guia_aerea_filtro_repository, self.interviniente_service, self.conf_service, self.confianza_extraccion_repository, self.guia_aerea_interviniente_service, self.notificacion_service, self.manifiesto_repository, self.auditoria_service, self.irregularidad_service)
        self.manifiesto_service = ManifiestoServiceImpl(self.manifiesto_repository, self.guia_aerea_service)
            
       