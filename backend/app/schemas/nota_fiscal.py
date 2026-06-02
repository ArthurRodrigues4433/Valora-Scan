from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class NotaFiscalBase(BaseModel):
    mercado_nome: str
    valor_total: float
    data_compra: datetime
    qr_code: Optional[str] = None

class NotaFiscalCreate(NotaFiscalBase):
    feira_id: int

class NotaFiscalUpdate(BaseModel):
    mercado_nome: Optional[str] = None
    valor_total: Optional[float] = None
    data_compra: Optional[datetime] = None
    qr_code: Optional[str] = None

class NotaFiscalSchema(NotaFiscalBase):
    id: int
    feira_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)