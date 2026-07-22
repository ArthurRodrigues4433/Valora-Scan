from pydantic import BaseModel, ConfigDict
from typing import Optional


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str


class UsuarioSchema(BaseModel):
    id: int
    nome: str
    email: str
    ativo: Optional[bool]
    admin: Optional[bool]

    model_config = ConfigDict(from_attributes=True)