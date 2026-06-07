from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProdutoExtraido(BaseModel):
    nome: Optional[str] = None
    preco_varejo: Optional[float] = None
    preco_atacado: Optional[float] = None
    qtd_minima_atacado: Optional[int] = None
    unidade_medida: Optional[str] = None


class OCRResponse(BaseModel):
    texto_extrato: str
    produto: ProdutoExtraido
    confianca: float
