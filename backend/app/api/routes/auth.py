from fastapi import APIRouter, HTTPException, Depends
from fastapi import Form
from app.models.usuario import Usuario
from app.core.database import db, pegar_session
from app.services.auth_service import (
    hash_password,
    authenticate_user,
    create_access_token,
)
from app.dependencies.auth import verify_token
from app.schemas.usuario import UsuarioCreate
from app.schemas.auth import LoginSchema
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register")
async def register(
    usuario_create: UsuarioCreate, session: Session = Depends(pegar_session)
):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_create.email).first()  # type: ignore
    if usuario:
        raise HTTPException(status_code=400, detail="Usuario já existe")
    else:
        senha_criptografada = hash_password(usuario_create.senha)
        novo_usuario = Usuario(nome=usuario_create.nome, email=usuario_create.email, senha=senha_criptografada, ativo=usuario_create.ativo, admin=usuario_create.admin)  # type: ignore
        session.add(novo_usuario)
        session.commit()
        raise HTTPException(status_code=201, detail="Usuario registrado com sucesso")


@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_session)):
    usuario = authenticate_user(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(
            status_code=400, detail="Usuario não encontrado ou senha incorreta"
        )
    else:
        access_token = create_access_token(id_usuario=usuario.id)  # type: ignore
        refresh_token = create_access_token(
            id_usuario=usuario.id, duration_token=timedelta(days=7)  # type: ignore
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }


@auth_router.post("/login-form")
async def login_form(
    dados_form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(pegar_session),
):
    usuario = authenticate_user(dados_form.username, dados_form.password, session)
    if not usuario:
        raise HTTPException(
            status_code=400, detail="Usuario não encontrado ou senha incorreta"
        )
    else:
        access_token = create_access_token(id_usuario=usuario.id) #type: ignore
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }


@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verify_token)):
    access_token = create_access_token(usuario.id)  # type: ignore
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
