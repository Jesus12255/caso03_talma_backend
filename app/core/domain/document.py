from sqlalchemy import Column, String, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class Document(Base):
    __tablename__ = "document"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(255), nullable=True)
    fields = Column(JSONB, nullable=True)
    file_name = Column(String(200), nullable=True)
    is_anonymized = Column(Boolean, nullable=True)
    created = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    enabled = Column(Boolean, server_default="true", nullable=False)