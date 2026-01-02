from sqlalchemy import Column, String, Integer, Boolean, Numeric, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from app.core.domain.base_model import Base

class GuiaAereaDataGrid(Base):
    __tablename__ = 'guia_aerea1_view'
    
    guia_aerea_id = Column(UUID(as_uuid=True), primary_key=True)
    
    # Mapped to remitente_gai_id from view
    remitente_id = Column("remitente_gai_id", UUID(as_uuid=True)) 
    nombre_remitente = Column(String)
    direccion_remitente = Column(String)
    telefono_remitente = Column(String)
    ciudad_remitente = Column(String)
    pais_remitente = Column(String)

    # Mapped to consignatario_gai_id from view
    consignatario_id = Column("consignatario_gai_id", UUID(as_uuid=True))
    nombre_consignatario = Column(String)
    direccion_consignatario = Column(String)
    telefono_consignatario = Column(String)
    ciudad_consignatario = Column(String)
    pais_consignatario = Column(String)

    numero = Column(String)
    tipo_codigo = Column(String)
    tipo = Column(String)
    fecha_emision = Column(TIMESTAMP(timezone=False))
    origen_codigo = Column(String)
    destino_codigo = Column(String)
    transbordo = Column(String)
    aerolinea_codigo = Column(String)
    numero_vuelo = Column(String)
    fecha_vuelo = Column(TIMESTAMP(timezone=False))
    descripcion_mercancia = Column(Text)
    cantidad_piezas = Column(Integer)
    peso_bruto = Column(Numeric)
    peso_cobrado = Column(Numeric)
    unidad_peso_codigo = Column(String)
    volumen = Column(Numeric)
    naturaleza_carga_codigo = Column(String)
    valor_declarado = Column(Numeric)
    tipo_flete_codigo = Column(String)
    tarifa_flete = Column(Numeric)
    otros_cargos = Column(Numeric)
    moneda_codigo = Column(String)
    total_flete = Column(Numeric)
    instrucciones_especiales = Column(Text)
    observaciones = Column(Text)
    estado_registro_codigo = Column(String)
    confidence_total_pct = Column(String)
    estado_confianza_codigo = Column(String)
    estado_confianza = Column(String)
    estado_registro = Column(String)
    habilitado = Column(Boolean)
    fecha_consulta = Column(TIMESTAMP(timezone=False))
