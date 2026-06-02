from typing import Optional
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Feira(Base):
    __tablename__ = "feiras"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    orcamento = Column(DECIMAL(10, 2), nullable=False)
    valor_previsto = Column(DECIMAL(10, 2), nullable=True)
    status = Column(String, default="em_andamento")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Relationships
    usuario = relationship("Usuario", back_populates="feiras", )
    feira_itens = relationship("FeiraItem", back_populates="feira", cascade="all, delete-orphan")
    notas_fiscais = relationship("NotaFiscal", back_populates="feira", cascade="all, delete-orphan")