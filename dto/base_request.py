from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from utl.constantes import Constantes


class BaseRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start: int = Field(default=Constantes.PAGINATION_START)
    limit: int = Field(default=Constantes.PAGINATION_SIZE)
    sort: Optional[str] = None
    palabraClave: Optional[str] = None
    totalCount: Optional[int] = None
