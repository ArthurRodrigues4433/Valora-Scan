from sqlalchemy.orm import Session
from decimal import Decimal
from sqlalchemy import func
from app.models.feira import Feira
from app.models.nota_fiscal import NotaFiscal
from app.models.feira_item import FeiraItem
from datetime import datetime
from typing import List


def listar_feiras_resumo(usuario_id: int, session: Session) -> list[dict]:
    feiras_db = session.query(Feira).filter(Feira.usuario_id == usuario_id).all()

    result = []
    for feira in feiras_db:
        gasto_real = (
            session.query(func.coalesce(func.sum(FeiraItem.subtotal), Decimal("0")))
            .filter(FeiraItem.feira_id == feira.id)
            .scalar()
        )

        orcamento = Decimal(str(feira.orcamento))
        gasto_real = Decimal(str(gasto_real)) if gasto_real else Decimal("0")

        economia = float(orcamento - gasto_real)
        progresso = float((gasto_real / orcamento) * 100) if orcamento > 0 else 0

        agora = datetime.utcnow()
        if feira.created_at.date() == agora.date():
            data_str = f"Hoje, {feira.created_at.strftime('%H:%M')}"
        else:
            data_str = feira.created_at.strftime("%a, %H:%M")

        result.append(
            {
                "id": feira.id,
                "nome": feira.nome,
                "data": data_str,
                "status": feira.status,
                "economia": round(economia, 2),
                "gasto_atual": float(gasto_real),
                "gasto_total": float(orcamento),
                "progresso": round(progresso, 0),
            }
        )

    return result


def obter_feira_detalhe(feira_id: int, usuario_id: int, session: Session) -> dict:
    feira_db = session.query(Feira).filter(Feira.id == feira_id).first()
    if not feira_db:
        raise ValueError("Feira não encontrada")
    if feira_db.usuario_id != usuario_id:
        raise ValueError("Acesso negado")

    gasto_total = float(feira_db.orcamento)

    if feira_db.created_at.date() == datetime.utcnow().date():
        data_str = f"Hoje, {feira_db.created_at.strftime('%H:%M')}"
    else:
        data_str = feira_db.created_at.strftime("%a, %H:%M")

    itens_db = session.query(FeiraItem).filter(FeiraItem.feira_id == feira_id).all()

    itens = []
    for item in itens_db:
        preco = float(item.preco_escolhido)
        preco_normal = float(item.preco_varejo)
        economia = max(0, preco_normal - preco) if preco_normal > preco else 0.0
        tipo = "atacado" if item.preco_atacado and float(item.preco_atacado) <= float(item.preco_varejo) else "varejo"

        itens.append(
            {
                "id": item.id,
                "nome": item.nome,
                "preco_escolhido": preco,
                "preco_varejo": preco_normal,
                "preco_atacado": (
                    float(item.preco_atacado) if item.preco_atacado else None
                ),
                "qtd_minima_atacado": item.qtd_minima_atacado,
                "quantidade": item.quantidade,
                "subtotal": float(item.subtotal),
                "unidade_medida": item.unidade_medida,
                "tempo": item.created_at.strftime("%H:%M"),
                "tipo": tipo,
                "economia": economia,
            }
        )

    return {
        "id": feira_db.id,
        "nome": feira_db.nome,
        "data": data_str,
        "gasto_total": gasto_total,
        "status": feira_db.status,
        "itensScaneados": len(itens),
        "itens": itens,
    }
