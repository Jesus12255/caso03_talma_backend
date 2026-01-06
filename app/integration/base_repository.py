from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any, Union
from app.core.domain.base_model import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(ABC, Generic[ModelType]):

    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        pass

    @abstractmethod
    async def save(self, obj_in: ModelType) -> ModelType:
        pass

    @abstractmethod
    async def save_all(self, objs: List[ModelType]) -> List[ModelType]:
        pass

    @abstractmethod
    async def update(self, id: Any, obj_in: Union[dict, ModelType]) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        pass
    