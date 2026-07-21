from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.dependencies.auth import verify_token
from app.models.usuario import Usuario
from app.models.feira import Feira
from app.models.feira_item import FeiraItem
from app.schemas.usuario import UsuarioSchema
from app.core.database import pegar_session
from decimal import Decimal

perfil_router = APIRouter(prefix="/perfil", tags=["perfil"])


class NomeUpdateSchema:
    nome: str


@perfil_router.get("/resumo")
async def get_perfil_resumo(
    usuario: Usuario = Depends(verify_token),
    session: Session = Depends(pegar_session),
):
    usuario_data = UsuarioSchema.from_orm(usuario)

    total_feiras = (
        session.query(func.count(Feira.id))
        .filter(Feira.usuario_id == usuario.id)
        .scalar()
    ) or 0

    feiras_finalizadas = (
        session.query(func.count(Feira.id))
        .filter(Feira.usuario_id == usuario.id, Feira.status == "finalizada")
        .scalar()
    ) or 0

    total_gasto = (
        session.query(func.coalesce(func.sum(Feira.orcamento), Decimal("0")))
        .filter(Feira.usuario_id == usuario.id)
        .scalar()
    )

    total_itens = (
        session.query(func.count(FeiraItem.id))
        .join(Feira, FeiraItem.feira_id == Feira.id)
        .filter(Feira.usuario_id == usuario.id)
        .scalar()
    ) or 0

    total_economia = (
        session.query(func.coalesce(func.sum(FeiraItem.subtotal), Decimal("0")))
        .join(Feira, FeiraItem.feira_id == Feira.id)
        .filter(
            Feira.usuario_id == usuario.id,
            FeiraItem.preco_escolhido < FeiraItem.preco_varejo,
        )
        .scalar()
    ) or Decimal("0")

    return {
        "usuario": usuario_data,
        "estatisticas": {
            "total_feiras": int(total_feiras),
            "feiras_finalizadas": int(feiras_finalizadas),
            "total_gasto": float(total_gasto),
            "total_itens": int(total_itens),
            "total_economia": float(total_economia),
        },
    }


@perfil_router.put("/nome", response_model=UsuarioSchema)
async def atualizar_nome(
    nome_data: dict,
    usuario: Usuario = Depends(verify_token),
    session: Session = Depends(pegar_session),
):
    usuario_db = session.query(Usuario).filter(Usuario.id == usuario.id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    novo_nome = nome_data.get("nome", "").strip()
    if not novo_nome:
        raise HTTPException(status_code=400, detail="Nome nao pode ser vazio")

    usuario_db.nome = novo_nome
    session.commit()
    session.refresh(usuario_db)

    return usuario_db
