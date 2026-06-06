from fastapi import APIRouter, Depends
from app.models.usuario import Usuario
from app.dependencies.auth import verify_token
from app.core.database import pegar_session
from app.services.relatorio_service import listar_ultimos_scans
from sqlalchemy.orm import Session

notas_router = APIRouter(
    prefix="/notas", tags=["notas"], dependencies=[Depends(verify_token)]
)


@notas_router.get("/scans")
async def listar_scans(
    session: Session = Depends(pegar_session), usuario: Usuario = Depends(verify_token)
):
    return listar_ultimos_scans(usuario.id, session)
