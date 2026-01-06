from typing import Type, List, Optional, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.inspection import inspect
from app.integration.base_repository import BaseRepository, ModelType


class BaseRepositoryImpl(BaseRepository[ModelType]):

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        pk_column = inspect(self.model).primary_key[0]
        query = select(self.model).where(pk_column == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def save(self, obj_in: ModelType) -> ModelType:
        pk_column = inspect(self.model).primary_key[0]
        pk_name = pk_column.name

        obj_id = getattr(obj_in, pk_name, None)

        if obj_id:
            existing_obj = await self.get_by_id(obj_id)
            if existing_obj:
                return await self.update(obj_id, obj_in)
        
        return await self.create(obj_in)

    async def create(self, obj_in: ModelType) -> ModelType:
        self.db.add(obj_in)
        await self.db.commit()
        await self.db.refresh(obj_in)
        return obj_in

    async def save_all(self, objs: List[ModelType]) -> List[ModelType]:
        self.db.add_all(objs)
        await self.db.commit()
        # Opcional: Refresh si se necesitan los IDs generados
        # for obj in objs:
        #     await self.db.refresh(obj)
        return objs

    async def update(self, id: Any, obj_in: Union[dict, ModelType]) -> Optional[ModelType]:
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.__dict__
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field) and value is not None and not field.startswith('_'):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> bool:
        db_obj = await self.get_by_id(id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
            return True
        return False