from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field
from utl.constantes import Constantes


T = TypeVar("T")
class CollectionResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    elements: List[T]
    start: Optional[int] = None
    sort: Optional[str] = None
    limit: int = Field(default=Constantes.PAGINATION_SIZE)
    totalCount: Optional[int] = None
