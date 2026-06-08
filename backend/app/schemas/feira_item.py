from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class FeiraItemBase(BaseModel):
    nome: str
    categoria: Optional[str] = None
    preco_varejo: float
    preco_atacado: Optional[float] = None
    qtd_minima_atacado: Optional[int] = None
    quantidade: int = 1
    unidade_medida: Optional[str] = None
    imagem_url: Optional[str] = None
    ocr_texto: Optional[str] = None

class FeiraItemCreate(FeiraItemBase):
    pass

class FeiraItemUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    preco_varejo: Optional[float] = None
    preco_atacado: Optional[float] = None
    qtd_minima_atacado: Optional[int] = None
    quantidade: Optional[int] = None
    unidade_medida: Optional[str] = None
    imagem_url: Optional[str] = None

class FeiraItemSchema(FeiraItemBase):
    id: int
    preco_escolhido: float
    subtotal: float
    feira_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)