from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi import Form
from fastapi.responses import JSONResponse
from app.models.usuario import Usuario
from app.core.database import db, pegar_session
from app.services.auth_service import (
    hash_password,
    authenticate_user,
    create_access_token,
    create_refresh_token,
)
from app.dependencies.auth import verify_token, verify_refresh_token
from app.schemas.usuario import UsuarioCreate
from app.schemas.auth import LoginSchema
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from app.main import limiter

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register")
@limiter.limit("5/minute")
async def register(
    request: Request,
    usuario_create: UsuarioCreate, session: Session = Depends(pegar_session)
):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_create.email).first()  # type: ignore
    if usuario:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    senha_criptografada = hash_password(usuario_create.senha)
    novo_usuario = Usuario(
        nome=usuario_create.nome,
        email=usuario_create.email,
        senha=senha_criptografada,
        ativo=True,
        admin=False,
    )  # type: ignore
    session.add(novo_usuario)
    session.commit()
    session.refresh(novo_usuario)
    return JSONResponse(
        status_code=201,
        content={"message": "Usuário registrado com sucesso", "id": novo_usuario.id}
    )


@auth_router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, login_schema: LoginSchema, session: Session = Depends(pegar_session)):
    usuario = authenticate_user(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )
    access_token = create_access_token(id_usuario=usuario.id)  # type: ignore
    refresh_token = create_refresh_token(id_usuario=usuario.id)  # type: ignore
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@auth_router.post("/login-form")
@limiter.limit("5/minute")
async def login_form(
    request: Request,
    dados_form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(pegar_session),
):
    usuario = authenticate_user(dados_form.username, dados_form.password, session)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )
    access_token = create_access_token(id_usuario=usuario.id)  # type: ignore
    refresh_token = create_refresh_token(id_usuario=usuario.id)  # type: ignore
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verify_refresh_token)):
    access_token = create_access_token(usuario.id)  # type: ignore
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
