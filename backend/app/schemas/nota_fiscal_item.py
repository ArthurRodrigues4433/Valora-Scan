from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class NotaFiscalItemBase(BaseModel):
    produto_nome: str
    quantidade: int
    preco_unitario: float
    preco_total: float

class NotaFiscalItemCreate(NotaFiscalItemBase):
    pass

class NotaFiscalItemUpdate(BaseModel):
    produto_nome: Optional[str] = None
    quantidade: Optional[int] = None
    preco_unitario: Optional[float] = None
    preco_total: Optional[float] = None
    divergencia: Optional[bool] = None
    valor_esperado: Optional[float] = None
    diferenca: Optional[float] = None

class NotaFiscalItemSchema(NotaFiscalItemBase):
    id: int
    divergencia: bool
    valor_esperado: Optional[float]
    diferenca: Optional[float]
    nota_fiscal_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)