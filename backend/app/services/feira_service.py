from sqlalchemy.orm import Session
from decimal import Decimal
from sqlalchemy import func
from app.models.feira import Feira
from app.models.nota_fiscal import NotaFiscal
from datetime import datetime


def listar_feiras_resumo(usuario_id: int, session: Session) -> list[dict]:
    feiras_db = session.query(Feira).filter(Feira.usuario_id == usuario_id).all()

    result = []
    for feira in feiras_db:
        gasto_real = (
            session.query(func.coalesce(func.sum(NotaFiscal.valor_total), Decimal("0")))
            .filter(NotaFiscal.feira_id == feira.id)
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
