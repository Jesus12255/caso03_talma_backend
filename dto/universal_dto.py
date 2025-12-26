from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional
from typing import List

class BaseOperacionResponse(BaseModel):
    codigo: str
    mensaje: str 

class ComboResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:  Optional[UUID] = None
    codigo: Optional[str] = None
    nombre: Optional[str] = None


class ComboBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    list: List[ComboResponse]
    size: int = Field(default=0)

   



