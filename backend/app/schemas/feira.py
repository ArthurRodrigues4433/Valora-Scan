from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class FeiraItemDetalheSchema(BaseModel):
    id: int
    nome: str
    preco_escolhido: float
    preco_varejo: float
    preco_atacado: Optional[float]
    qtd_minima_atacado: int
    quantidade: int
    subtotal: float
    unidade_medida: str
    tempo: str
    tipo: str
    economia: float

    model_config = ConfigDict(from_attributes=True)


class FeiraDetalheSchema(BaseModel):
    id: int
    nome: str
    data: str
    gasto_total: float
    status: str
    itensScaneados: int
    itens: List[FeiraItemDetalheSchema]

    model_config = ConfigDict(from_attributes=True)


class FeiraCreate(BaseModel):
    nome: str
    orcamento: float = Field(gt=0, description="Orçamento deve ser maior que zero")


class FeiraUpdate(BaseModel):
    nome: Optional[str] = None
    orcamento: Optional[float] = None
    status: Optional[str] = None


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
    data: str
    status: str
    economia: float
    gasto_atual: float
    gasto_total: float
    progresso: float

    model_config = ConfigDict(from_attributes=True)
