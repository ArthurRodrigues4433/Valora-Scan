from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class NotaFiscal(Base):
    __tablename__ = "notas_fiscais"

    id = Column(Integer, primary_key=True, index=True)
    mercado_nome = Column(String, nullable=False)
    valor_total = Column(DECIMAL(10, 2), nullable=False)
    data_compra = Column(DateTime, nullable=False)
    qr_code = Column(String, nullable=True)
    consentimento_lgpd = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign key
    feira_id = Column(Integer, ForeignKey("feiras.id"), nullable=False)

    # Relationships
    feira = relationship("Feira", back_populates="notas_fiscais")
    nota_fiscal_itens = relationship("NotaFiscalItem", back_populates="nota_fiscal", cascade="all, delete-orphan")