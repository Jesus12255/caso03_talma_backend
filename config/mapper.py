from typing import Type, Any
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeMeta

class Mapper:
    @staticmethod
    def to_dto(entity: Any, dto_class: Type[BaseModel]):
        return dto_class.from_orm(entity)

    @staticmethod
    def to_entity(dto: BaseModel, entity_class: Type[DeclarativeMeta]):
        valid_fields = {c.name for c in entity_class.__table__.columns}
        filtered_data = {k: v for k, v in dto.model_dump().items() if k in valid_fields}
        return entity_class(**filtered_data)
