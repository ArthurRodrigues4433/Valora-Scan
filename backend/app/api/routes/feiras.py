from fastapi import APIRouter, HTTPException, Depends
from app.models.feira import Feira
from app.core.database import db, pegar_session
from app.schemas.feira import FeiraCreate
from app.schemas.auth import LoginSchema
from sqlalchemy.orm import Session

feiras_router = APIRouter(prefix="/feiras", tags=["feiras"])


@feiras_router.get("/")
async def listar_feiras():
    return {"message": "Listando feiras"}


@feiras_router.post("/feira")
async def criar_feira(
    feiraSchema: FeiraCreate, session: Session = Depends(pegar_session)
):
    feira_db = session.query(Feira).filter(Feira.nome == feiraSchema.nome).first()  # type: ignore
    if feira_db:
        raise HTTPException(status_code=400, detail="Feira já existe")
    else:
        nova_feira = Feira(nome=feiraSchema.nome, orcamento=feiraSchema.orcamento, usuario_id=feiraSchema.usuario_id)  # type: ignore
        session.add(nova_feira)
        session.commit()

    return {"message": "Feira criada com sucesso"}
