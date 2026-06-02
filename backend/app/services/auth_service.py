from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.models.usuario import Usuario
from app.core.database import db
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)


def authenticate_user(email, senha, session: Session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):  # type: ignore
        return False

    return usuario


def create_access_token(
    id_usuario: int, duration_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
):
    date_expires = datetime.now(timezone.utc) + duration_token
    dict_info = {"sub": id_usuario, "exp": date_expires}
    encoded_jwt = jwt.encode(dict_info, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore
    return encoded_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
        usuario_id = payload.get("sub")
        if usuario_id is None:
            raise JWTError("Token inválido")
        return usuario_id
    except JWTError:
        raise
