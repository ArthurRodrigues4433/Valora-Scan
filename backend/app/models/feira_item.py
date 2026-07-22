from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class FeiraItem(Base):
    __tablename__ = "feira_itens"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=True)
    preco_varejo = Column(DECIMAL(10, 2), nullable=False)
    preco_atacado = Column(DECIMAL(10, 2), nullable=True)
    qtd_minima_atacado = Column(Integer, nullable=True)
    quantidade = Column(Integer, nullable=False)
    preco_escolhido = Column(DECIMAL(10, 2), nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    unidade_medida = Column(String, nullable=True)
    imagem_url = Column(String, nullable=True)
    ocr_texto = Column(String, nullable=True)
    ean = Column(String, nullable=True, index=True)
    cod_interno = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign key
    feira_id = Column(Integer, ForeignKey("feiras.id"), nullable=False)

    # Relationship
    feira = relationship("Feira", back_populates="feira_itens")