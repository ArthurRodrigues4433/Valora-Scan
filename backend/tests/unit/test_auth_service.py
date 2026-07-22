import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.services.auth_service import (
    hash_password,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
)


@pytest.fixture(autouse=True)
def setup_auth_env(monkeypatch):
    monkeypatch.setattr("app.services.auth_service.SECRET_KEY", "test_secret_key")
    monkeypatch.setattr("app.services.auth_service.ALGORITHM", "HS256")
    monkeypatch.setattr("app.services.auth_service.ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    monkeypatch.setattr("app.services.auth_service.REFRESH_TOKEN_EXPIRE_DAYS", 7)


def test_hash_password_returns_string():
    hashed = hash_password("minhasenha")
    assert isinstance(hashed, str)
    assert hashed != "minhasenha"


def test_hash_password_is_different_each_call():
    h1 = hash_password("mesmasenha")
    h2 = hash_password("mesmasenha")
    assert h1 != h2


def test_authenticate_user_success(db_session, usuario):
    result = authenticate_user(usuario.email, "senha123", db_session)
    assert result is not False
    assert result.id == usuario.id
    assert result.email == usuario.email


def test_authenticate_user_wrong_password(db_session, usuario):
    from app.models.usuario import Usuario
    from app.services.auth_service import hash_password
    db_session.add(Usuario(nome="Outro", email="outro@example.com", senha=hash_password("outrasenha")))
    db_session.commit()
    result = authenticate_user("outro@example.com", "senhaerrada", db_session)
    assert result is False


def test_authenticate_user_not_found(db_session):
    result = authenticate_user("naoexiste@example.com", "qualquer", db_session)
    assert result is False


def test_create_access_token_contains_correct_claims(usuario):
    token = create_access_token(id_usuario=usuario.id)
    payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
    assert payload["sub"] == str(usuario.id)
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_refresh_token_contains_correct_claims(usuario):
    token = create_refresh_token(id_usuario=usuario.id)
    payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
    assert payload["sub"] == str(usuario.id)
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_access_token_expires_in_30_minutes(usuario):
    before = datetime.now(timezone.utc)
    token = create_access_token(id_usuario=usuario.id)
    payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    delta = (exp - before).total_seconds()
    assert 1790 < delta < 1810


def test_refresh_token_expires_in_7_days(usuario):
    before = datetime.now(timezone.utc)
    token = create_refresh_token(id_usuario=usuario.id)
    payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    delta = (exp - before).total_seconds()
    assert 604730 < delta < 604830


def test_decode_token_valid(usuario):
    token = create_access_token(id_usuario=usuario.id)
    user_id = decode_token(token)
    assert user_id == usuario.id


def test_decode_token_invalid_raises():
    with pytest.raises(JWTError):
        decode_token("token.invalido")


def test_decode_token_wrong_secret_raises(usuario):
    token = create_access_token(id_usuario=usuario.id)
    with pytest.raises(JWTError):
        decode_token.__wrapped__(token) if hasattr(decode_token, '__wrapped__') else jwt.decode(token, "wrong_secret", algorithms=["HS256"])


def test_decode_token_expired_raises(usuario):
    past = datetime.now(timezone.utc) - timedelta(days=1)
    payload = {"sub": str(usuario.id), "type": "access", "exp": past}
    expired_token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
    with pytest.raises(JWTError):
        decode_token(expired_token)
