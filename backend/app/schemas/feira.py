from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class FeiraCreate(BaseModel):
    nome: str
    orcamento: float


class FeiraUpdate(BaseModel):
    nome: Optional[str] = None
    orcamento: Optional[float] = None


class FeiraSchema(BaseModel):
    id: int
    usuario_id: int
    nome: str
    orcamento: float
    valor_previsto: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FeiraResumoSchema(BaseModel):
    id: int
    nome: str
    economia: float
    gasto_atual: float
    gasto_total: float
    progresso: float

    model_config = ConfigDict(from_attributes=True)
