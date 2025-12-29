from sqlalchemy import Column, String, Boolean, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    habilitado = Column(Boolean, default=True, nullable=True)
    creado = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    creado_por = Column(String, nullable=True)
    modificado = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())
    modificado_por = Column(String, nullable=True)