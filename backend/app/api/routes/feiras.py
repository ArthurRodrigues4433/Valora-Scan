from fastapi import APIRouter, HTTPException, Depends
from app.models.feira import Feira
from app.models.usuario import Usuario
from app.core.database import db, pegar_session
from app.dependencies.auth import verify_token
from app.schemas.feira import FeiraCreate, FeiraUpdate, FeiraSchema
from app.schemas.auth import LoginSchema
from sqlalchemy.orm import Session

feiras_router = APIRouter(
    prefix="/feiras", tags=["feiras"], dependencies=[Depends(verify_token)]
)


@feiras_router.get("/")
async def listar_feiras():
    return {"message": "Listando feiras"}


@feiras_router.post("/feira")
async def criar_feira(
    feiraSchema: FeiraCreate,
    session: Session = Depends(pegar_session),
    usuario: Usuario = Depends(verify_token),
):
    feira_db = session.query(Feira).filter(Feira.nome == feiraSchema.nome).first()  # type: ignore
    if feira_db:
        raise HTTPException(status_code=400, detail="Feira já existe")
    else:
        nova_feira = Feira(
            nome=feiraSchema.nome,
            orcamento=feiraSchema.orcamento,
            usuario_id=usuario.id,
        )  # type: ignore
        session.add(nova_feira)
        session.commit()

    return {"message": "Feira criada com sucesso"}


@feiras_router.put("/feira/{id}")
async def atualizar_feira(
    id: int,
    feira_update: FeiraUpdate,
    session: Session = Depends(pegar_session),
    usuario: Usuario = Depends(verify_token),
):
    feira_db = session.query(Feira).filter(Feira.id == id).first()  # type: ignore
    if not feira_db:
        raise HTTPException(status_code=404, detail="Feira não encontrada")
    if feira_db.usuario_id != usuario.id:  # type: ignore
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if feira_db.status == "finalizada":
        raise HTTPException(status_code=400, detail="Feira já finalizada, não pode ser editada")

    if feira_update.nome is not None:
        feira_db.nome = feira_update.nome
    if feira_update.orcamento is not None:
        feira_db.orcamento = feira_update.orcamento

    session.commit()
    session.refresh(feira_db)
    return {"message": "Feira atualizada com sucesso"}


@feiras_router.delete("/feira/{id}")
async def deletar_feira(
    id: int,
    session: Session = Depends(pegar_session),
    usuario: Usuario = Depends(verify_token),
):
    feira_db = session.query(Feira).filter(Feira.id == id).first()  # type: ignore
    if not feira_db:
        raise HTTPException(status_code=404, detail="Feira não encontrada")
    if feira_db.usuario_id != usuario.id:  # type: ignore
        raise HTTPException(status_code=403, detail="Acesso negado")

    session.delete(feira_db)
    session.commit()
    return {"message": "Feira deletada com sucesso"}
