from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.feira import Feira
from app.models.nota_fiscal import NotaFiscal
from app.models.nota_fiscal_item import NotaFiscalItem
from app.models.feira_item import FeiraItem


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
        session.query(func.coalesce(func.sum(FeiraItem.subtotal), Decimal("0")))
        .join(Feira, FeiraItem.feira_id == Feira.id)
        .filter(
            Feira.usuario_id == usuario_id,
            FeiraItem.created_at >= primeiro_dia_mes,
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
        session.query(func.count(FeiraItem.id))
        .join(Feira, FeiraItem.feira_id == Feira.id)
        .filter(
            Feira.usuario_id == usuario_id,
            FeiraItem.created_at >= primeiro_dia_mes,
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


def listar_ultimos_scans(
    usuario_id: int, session: Session, limit: int = 5
) -> list[dict]:
    scans_db = (
        session.query(FeiraItem)
        .join(Feira, FeiraItem.feira_id == Feira.id)
        .filter(Feira.usuario_id == usuario_id)
        .order_by(FeiraItem.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    agora = datetime.utcnow()

    for item in scans_db:
        diff = agora - item.created_at
        if diff < timedelta(minutes=1):  # type: ignore
            tempo_str = "Agora"
        elif diff < timedelta(hours=1):  # type: ignore
            mins = int(diff.total_seconds() / 60)
            tempo_str = f"{mins} min atrás"
        elif diff < timedelta(days=1):  # type: ignore
            hours = int(diff.total_seconds() / 3600)
            tempo_str = f"{hours}h atrás"
        else:
            dias = diff.days
            tempo_str = f"{dias}d atrás"

        preco = float(item.preco_escolhido)
        preco_normal = float(item.preco_varejo)
        economia = max(0, preco_normal - preco) if preco_normal > preco else 0.0

        result.append(
            {
                "id": item.id,
                "nome": item.nome,
                "preco": preco,
                "economia": economia,
                "tempo": tempo_str,
            }
        )

    return result