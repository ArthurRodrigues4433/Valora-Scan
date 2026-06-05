from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal
from app.models.feira import Feira
from app.models.nota_fiscal import NotaFiscal
from app.models.nota_fiscal_item import NotaFiscalItem  # <-- adicionar


def calcular_economia_mensal(usuario_id: int, session: Session):
    agora = datetime.utcnow()
    primeiro_dia_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    orcamento_total = (
        session.query(func.coalesce(func.sum(Feira.orcamento), Decimal("0")))
        .filter(
            Feira.usuario_id == usuario_id,
            Feira.created_at >= primeiro_dia_mes,
        )
        .scalar()
    )

    gasto_real = (
        session.query(func.coalesce(func.sum(NotaFiscal.valor_total), Decimal("0")))
        .join(Feira, NotaFiscal.feira_id == Feira.id)
        .filter(
            Feira.usuario_id == usuario_id,
            NotaFiscal.data_compra >= primeiro_dia_mes,
        )
        .scalar()
    )

    orcamento_total = Decimal(orcamento_total)
    gasto_real = Decimal(gasto_real)

    economia = orcamento_total - gasto_real
    percentual = (
        float((economia / orcamento_total) * 100) if orcamento_total > 0 else 0.0
    )

    # Contagem de itens escaneados (NotaFiscalItem) no mês atual
    itens_escaneados = (
        session.query(func.count(NotaFiscalItem.id))
        .join(NotaFiscal, NotaFiscalItem.nota_fiscal_id == NotaFiscal.id)
        .join(Feira, NotaFiscal.feira_id == Feira.id)
        .filter(
            Feira.usuario_id == usuario_id,
            NotaFiscal.data_compra >= primeiro_dia_mes,
        )
        .scalar()
    ) or 0

    mes_formatado = agora.strftime("%Y-%m")

    return {
        "orcamento_total": orcamento_total,
        "gasto_real": gasto_real,
        "economia": economia,
        "percentual_economia": round(percentual, 1),
        "mes": mes_formatado,
        "comparacao_mes_anterior": None,
        "itens_escaneados": int(itens_escaneados),  # <-- adicionar
    }
