from pydantic import BaseModel

class BaseOperacionResponse(BaseModel):
    codigo: str
    mensaje: str 

