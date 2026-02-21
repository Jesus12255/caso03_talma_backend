from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from app.core.domain.base_model import BaseModel

class PerfilRiesgo(BaseModel):
    __tablename__ = "perfil_riesgo"

    perfil_riesgo_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identificación y Vínculos
    nombre_normalizado = Column(String(200), index=True, nullable=True)
    tipo_interviniente_codigo = Column(String(40), nullable=True) # SENDER, CONSIGNEE, etc.
    
    vector_identidad = Column(Vector(3072), nullable=True)
    
    variaciones_nombre = Column(JSON, default=list)
    telefonos_conocidos = Column(JSON, default=list)
    direcciones_conocidas = Column(JSON, default=list)
    
    # --- CAPA HISTÓRICA: MÉTRICAS DE PESO ---
    peso_promedio = Column(Float, default=0.0)
    peso_std_dev = Column(Float, default=0.0) # Desviación estándar para cálculo de Z-Score
    peso_maximo_historico = Column(Float, default=0.0)
    
    # --- CAPA HISTÓRICA: MÉTRICAS TEMPORALES Y FRECUENCIA ---
    cantidad_envios = Column(Integer, default=0)
    dias_promedio_entre_envios = Column(Integer, default=0)
    fecha_primer_envio = Column(DateTime, default=datetime.utcnow)
    fecha_ultimo_envio = Column(DateTime, onupdate=datetime.utcnow)
    es_perfil_durmiente = Column(Boolean, default=False) # True si lleva > 6 meses sin operar
    
    # --- CONTEXTO DE RED Y RUTAS ---
    rutas_frecuentes = Column(JSON, default=dict) # {"LIM-MIA": 15, "LIM-MAD": 2}
    total_consignatarios_vinculados = Column(Integer, default=0) # Para detectar pitufeo/distribución
    
    # --- REPUTACIÓN Y FEEDBACK LOOP ---
    score_base = Column(Integer, default=0) # Reputación inicial (0-100)
    total_alertas_generadas = Column(Integer, default=0)
    total_alertas_confirmadas = Column(Integer, default=0) # Para ajustar el falso positivo
    factor_tolerancia = Column(Float, default=1.0) # Reduce sensibilidad si es cliente confiable

    def __repr__(self):
        return f"<PerfilRiesgo(nombre='{self.nombre_normalizado}', envios={self.cantidad_envios}, score={self.score_base})>"