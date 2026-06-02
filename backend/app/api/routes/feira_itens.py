from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import pegar_session
from app.dependencies.auth import verify_token
from app.models.feira import Feira
from app.models.feira_item import FeiraItem
from app.schemas.feira_item import FeiraItemCreate, FeiraItemSchema, FeiraItemUpdate
from app.services.feira_item_service import (
    criar_item,
    atualizar_item,
    deletar_item,
)

feira_itens_router = APIRouter(
    prefix="/feiras",
    tags=["feira_itens"],
    dependencies=[Depends(verify_token)],
)


@feira_itens_router.post("/feira/{feira_id}/itens", response_model=FeiraItemSchema)
async def criar_item_feira(
    feira_id: int,
    item_data: FeiraItemCreate,
    session: Session = Depends(pegar_session),
    usuario=Depends(verify_token),
):
    feira = session.query(Feira).filter(Feira.id == feira_id).first()
    if not feira:
        raise HTTPException(status_code=404, detail="Feira não encontrada")
    if feira.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    item = criar_item(feira_id, item_data, session)
    return item


@feira_itens_router.get("/feira/{feira_id}/itens", response_model=List[FeiraItemSchema])
async def listar_itens_feira(
    feira_id: int,
    session: Session = Depends(pegar_session),
    usuario=Depends(verify_token),
):
    feira = session.query(Feira).filter(Feira.id == feira_id).first()
    if not feira:
        raise HTTPException(status_code=404, detail="Feira não encontrada")
    if feira.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    itens = session.query(FeiraItem).filter(FeiraItem.feira_id == feira_id).all()
    return itens


@feira_itens_router.patch(
    "/feira/{feira_id}/itens/{item_id}", response_model=FeiraItemSchema
)
async def atualizar_item_feira(
    feira_id: int,
    item_id: int,
    item_data: FeiraItemUpdate,
    session: Session = Depends(pegar_session),
    usuario=Depends(verify_token),
):
    feira = session.query(Feira).filter(Feira.id == feira_id).first()
    if not feira:
        raise HTTPException(status_code=404, detail="Feira não encontrada")
    if feira.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    item = atualizar_item(feira_id, item_id, item_data, session)
    return item


@feira_itens_router.delete("/feira/{feira_id}/itens/{item_id}")
async def deletar_item_feira(
    feira_id: int,
    item_id: int,
    session: Session = Depends(pegar_session),
    usuario=Depends(verify_token),
):
    feira = session.query(Feira).filter(Feira.id == feira_id).first()
    if not feira:
        raise HTTPException(status_code=404, detail="Feira não encontrada")
    if feira.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    return deletar_item(feira_id, item_id, session)
