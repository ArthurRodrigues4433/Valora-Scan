from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.services.auth_service import decode_token, oauth2_scheme
from app.core.database import pegar_session
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login-form")


def verify_token(token: str = Depends(oauth2_scheme), session: Session = Depends(pegar_session)):
    """
    Dependência do FastAPI para verificar token JWT e retornar o usuário autenticado.
    Decodifica o token e busca o usuário no banco de dados.
    """
    try:
        usuario_id = decode_token(token)
        usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise Exception("Usuário não encontrado")
        return usuario
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
