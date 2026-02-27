from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.core.domain.base_model import Base

class PerfilRiesgoDataGrid(Base):
    __tablename__ = "vw_perfil_riesgo"

    perfil_riesgo_id = Column(UUID(as_uuid=True), primary_key=True)
    
    nombre_normalizado = Column(String(200))
    tipo_interviniente_codigo = Column(String(40))
    tipo_interviniente = Column(String(100))
    
    variaciones_nombre = Column(JSON)
    telefonos_conocidos = Column(JSON)
    direcciones_conocidas = Column(JSON)
    
    peso_promedio = Column(Float)
    peso_std_dev = Column(Float)
    peso_maximo_historico = Column(Float)
    peso_minimo_historico = Column(Float)
    
    cantidad_envios = Column(Integer)
    dias_promedio_entre_envios = Column(Integer)
    fecha_primer_envio = Column(DateTime)
    fecha_ultimo_envio = Column(DateTime)
    
    rutas_frecuentes = Column(JSON)
    total_consignatarios_vinculados = Column(Integer)
    
    score_base = Column(Integer)
    factor_tolerancia = Column(Float)

    creado = Column(DateTime)
    habilitado = Column(Boolean)

    def __repr__(self):
        return f"<VwPerfilRiesgo(nombre='{self.nombre_normalizado}', tipo='{self.tipo_interviniente}')>"
