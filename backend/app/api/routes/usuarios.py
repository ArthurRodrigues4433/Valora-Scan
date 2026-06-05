from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.auth import verify_token
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioSchema
from app.core.database import pegar_session

usuarios_router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@usuarios_router.get("/me", response_model=UsuarioSchema)
async def get_me(usuario: Usuario = Depends(verify_token)):
    return usuario