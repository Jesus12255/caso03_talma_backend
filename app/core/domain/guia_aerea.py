from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    Numeric,
    Float
)
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.domain.base_model import BaseModel
from sqlalchemy.orm import  relationship
from app.core.domain.guia_aerea_interviniente import GuiaAereaInterviniente


class GuiaAerea(BaseModel):
    __tablename__ = "guia_aerea1"

    guia_aerea_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core Fields with Confidence
    numero = Column(String(20), nullable=False)
    confidence_numero = Column(Float, nullable=True)

    tipo_codigo = Column(String(40), nullable=True)

    fecha_emision = Column(TIMESTAMP(timezone=False), nullable=False)
    confidence_fecha_emision = Column(Float, nullable=True)

    origen_codigo = Column(String(40), nullable=False)
    confidence_origen_codigo = Column(Float, nullable=True)

    destino_codigo = Column(String(40), nullable=False)
    confidence_destino_codigo = Column(Float, nullable=True)

    transbordo = Column(String(200), nullable=True)
    confidence_transbordo = Column(Float, nullable=True)

    aerolinea_codigo = Column(String(40), nullable=True)
    confidence_aerolinea_codigo = Column(Float, nullable=True)

    numero_vuelo = Column(String(50), nullable=True)
    confidence_numero_vuelo = Column(Float, nullable=True)

    fecha_vuelo = Column(TIMESTAMP(timezone=False), nullable=True)
    confidence_fecha_vuelo = Column(Float, nullable=True)

    descripcion_mercancia = Column(Text, nullable=True)
    confidence_descripcion_mercancia = Column(Float, nullable=True)

    cantidad_piezas = Column(Integer, nullable=False)
    confidence_cantidad_piezas = Column(Float, nullable=True)

    peso_bruto = Column(Numeric(10, 3), nullable=True)
    confidence_peso_bruto = Column(Float, nullable=True)

    peso_cobrado = Column(Numeric(10, 3), nullable=True)
    confidence_peso_cobrado = Column(Float, nullable=True)

    unidad_peso_codigo = Column(String(40), nullable=True)
    confidence_unidad_peso_codigo = Column(Float, nullable=True)

    volumen = Column(Numeric(10, 3), nullable=True)
    confidence_volumen = Column(Float, nullable=True)

    naturaleza_carga_codigo = Column(String(40), nullable=True)
    confidence_naturaleza_carga_codigo = Column(Float, nullable=True)

    valor_declarado = Column(Numeric(14, 2), nullable=True)
    confidence_valor_declarado = Column(Float, nullable=True)

    tipo_flete_codigo = Column(String(40), nullable=True)
    confidence_tipo_flete_codigo = Column(Float, nullable=True)

    tarifa_flete = Column(Numeric(14, 2), nullable=True)
    confidence_tarifa_flete = Column(Float, nullable=True)

    otros_cargos = Column(Numeric(14, 2), nullable=True)
    confidence_otros_cargos = Column(Float, nullable=True)

    moneda_codigo = Column(String(40), nullable=False)
    confidence_moneda_codigo = Column(Float, nullable=True)

    total_flete = Column(Numeric(14, 2), nullable=False)
    confidence_total_flete = Column(Float, nullable=True)

    instrucciones_especiales = Column(Text, nullable=True)
    confidence_instrucciones_especiales = Column(Float, nullable=True)

    observaciones = Column(Text, nullable=True)
    confidence_observaciones = Column(Float, nullable=True)

    # Metadata & State
    confidence_total = Column(Float, nullable=True)
    estado_confianza_codigo  = Column(String(40), nullable=True)
    estado_registro_codigo = Column(String(40), nullable=False)

    # Relationships
    intervinientes = relationship(
        "GuiaAereaInterviniente",
        back_populates="guia_aerea",
        cascade="all, delete-orphan",
        primaryjoin="and_(GuiaAerea.guia_aerea_id==GuiaAereaInterviniente.guia_aerea_id, GuiaAereaInterviniente.es_version_activa==True)"
    )
