from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.auth import verify_token
from app.services.relatorio_service import calcular_economia_mensal
from app.schemas.relatorio import EconomiaMensalSchema
from app.core.database import pegar_session

relatorios_router = APIRouter(prefix="/relatorios", tags=["relatorios"])


@relatorios_router.get("/economia", response_model=EconomiaMensalSchema)
async def get_economia_mensal(
    usuario=Depends(verify_token),
    session: Session = Depends(pegar_session),
):
    resultado = calcular_economia_mensal(usuario.id, session)
    return resultado