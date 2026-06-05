from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal


class EconomiaMensalSchema(BaseModel):
    orcamento_total: Decimal
    gasto_real: Decimal
    economia: Decimal
    percentual_economia: float
    mes: str
    comparacao_mes_anterior: Optional[float] = None
    itens_escaneados: Optional[int] = None  # <-- adicionar

    model_config = ConfigDict(from_attributes=True)
