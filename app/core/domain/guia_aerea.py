from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    Numeric
)
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.domain.base_model import BaseModel
from sqlalchemy.orm import  relationship


class GuiaAerea(BaseModel):
    __tablename__ = "guia_aerea"

    guia_aerea_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    remitente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviniente.interviniente_id"),
        nullable=False
    )
    consignatario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviniente.interviniente_id"),
        nullable=False
    )

    numero = Column(String(20), nullable=False)
    tipo_codigo = Column(String(40), nullable=False)
    fecha_emision = Column(TIMESTAMP(timezone=False), nullable=False)
    estado_guia_codigo = Column(String(40), nullable=False)

    origen_codigo = Column(String(40), nullable=False)
    destino_codigo = Column(String(40), nullable=False)
    transbordo = Column(String(200), nullable=True)

    aerolinea_codigo = Column(String(40), nullable=True)
    numero_vuelo = Column(String(50), nullable=True)
    fecha_vuelo = Column(TIMESTAMP(timezone=False), nullable=True)

    descripcion_mercancia = Column(Text, nullable=True)
    cantidad_piezas = Column(Integer, nullable=False)

    peso_bruto = Column(Numeric(10, 3), nullable=True)
    peso_cobrado = Column(Numeric(10, 3), nullable=True)
    unidad_peso_codigo = Column(String(40), nullable=True)

    volumen = Column(Numeric(10, 3), nullable=True)
    naturaleza_carga_codigo = Column(String(40), nullable=True)
    valor_declarado = Column(Numeric(14, 2), nullable=True)

    tipo_flete_codigo = Column(String(40), nullable=True)
    tarifa_flete = Column(Numeric(14, 2), nullable=True)
    otros_cargos = Column(Numeric(14, 2), nullable=True)

    moneda_codigo = Column(String(40), nullable=False)
    total_flete = Column(Numeric(14, 2), nullable=False)

    instrucciones_especiales = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    estado_registro_codigo = Column(String(40), nullable=False)

    confidence_total = Column(Numeric(5, 2), nullable=True)
    estado_confianza_codigo  = Column(String(40), nullable=False)


    confianzas_extraccion = relationship(
        "ConfianzaExtraccion",
        back_populates="guia_aerea",
        cascade="all, delete-orphan"
    )

    interviniente_remitente = relationship(
        "Interviniente",
        foreign_keys=[remitente_id],
        lazy="select"
    )

    interviniente_consignatario = relationship(
        "Interviniente",
        foreign_keys=[consignatario_id],
        lazy="select"
    )