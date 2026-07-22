from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import os
from app.services.auth_service import oauth2_scheme
from app.core.database import pegar_session
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login-form")


def verify_token(token: str = Depends(oauth2_scheme), session: Session = Depends(pegar_session)):
    """
    Dependência do FastAPI para verificar token JWT e retornar o usuário autenticado.
    Decodifica o token e busca o usuário no banco de dados.
    """
    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM", "HS256")],
        )
        usuario_id = payload.get("sub")
        token_type = payload.get("type")

        if usuario_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return usuario
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_refresh_token(token: str = Depends(oauth2_scheme), session: Session = Depends(pegar_session)):
    """
    Dependência do FastAPI para verificar refresh token JWT e retornar o usuário autenticado.
    """
    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM", "HS256")],
        )
        usuario_id = payload.get("sub")
        token_type = payload.get("type")

        if usuario_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return usuario
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
