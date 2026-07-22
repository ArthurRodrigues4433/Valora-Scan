from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


class FeiraItemBase(BaseModel):
    nome: str
    categoria: Optional[str] = None
    preco_varejo: float = Field(gt=0, description="Preço de varejo deve ser maior que zero")
    preco_atacado: Optional[float] = Field(default=None, gt=0, description="Preço de atacado deve ser maior que zero")
    qtd_minima_atacado: Optional[int] = Field(default=None, gt=0, description="Quantidade mínima deve ser maior que zero")
    quantidade: int = Field(gt=0, description="Quantidade deve ser maior que zero")
    unidade_medida: Optional[str] = None
    imagem_url: Optional[str] = None
    ocr_texto: Optional[str] = None
    ean: Optional[str] = None
    cod_interno: Optional[str] = None

    @field_validator("ean")
    @classmethod
    def validar_ean(cls, v):
        if v is None or v == "":
            return v
        if not re.fullmatch(r"\d{8,14}", v):
            raise ValueError("EAN deve conter entre 8 e 14 dígitos numéricos")
        return v


class FeiraItemCreate(FeiraItemBase):
    pass

class FeiraItemUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    preco_varejo: Optional[float] = Field(default=None, gt=0)
    preco_atacado: Optional[float] = Field(default=None, gt=0)
    qtd_minima_atacado: Optional[int] = Field(default=None, gt=0)
    quantidade: Optional[int] = Field(default=None, gt=0)
    unidade_medida: Optional[str] = None
    imagem_url: Optional[str] = None
    ocr_texto: Optional[str] = None
    ean: Optional[str] = None
    cod_interno: Optional[str] = None

    @field_validator("ean")
    @classmethod
    def validar_ean(cls, v):
        if v is None or v == "":
            return v
        if not re.fullmatch(r"\d{8,14}", v):
            raise ValueError("EAN deve conter entre 8 e 14 dígitos numéricos")
        return v

class FeiraItemSchema(FeiraItemBase):
    id: int
    preco_escolhido: float
    subtotal: float
    feira_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)