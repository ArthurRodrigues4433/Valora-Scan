import pytest
from fastapi.testclient import TestClient


def get_token(client: TestClient, email: str, senha: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_acesso_rota_protegida_sem_token(client: TestClient):
    resp = client.get("/feiras/feira")
    assert resp.status_code == 401


def test_acesso_rota_protegida_com_token_expirado(client: TestClient, usuario):
    from jose import jwt
    from datetime import datetime, timedelta, timezone
    from app.services.auth_service import SECRET_KEY, ALGORITHM

    expired_payload = {
        "sub": str(usuario.id),
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    resp = client.get("/feiras/feira", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401


def test_idor_feira_outro_usuario(client: TestClient, usuario):
    # Cria feira para usuario
    token = get_token(client, usuario.email, "senha123")
    resp = client.post("/feiras/feira", headers={"Authorization": f"Bearer {token}"}, json={
        "nome": "Feira Privada",
        "orcamento": 100.0
    })
    assert resp.status_code == 200
    feiras = client.get("/feiras/feira", headers={"Authorization": f"Bearer {token}"}).json()
    feira_id = feiras[0]["id"]

    # Segundo usuário tenta acessar
    client.post("/auth/register", json={
        "nome": "Outro",
        "email": "outro_idor@example.com",
        "senha": "SenhaForte123"
    })
    token2 = get_token(client, "outro_idor@example.com", "SenhaForte123")

    resp = client.get(f"/feiras/feira/{feira_id}", headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 403


def test_idor_item_outro_usuario(client: TestClient, usuario, feira, item_feira):
    token = get_token(client, usuario.email, "senha123")

    client.post("/auth/register", json={
        "nome": "Atacante",
        "email": "atacante@teste.com",
        "senha": "SenhaForte123"
    })
    token2 = get_token(client, "atacante@teste.com", "SenhaForte123")

    resp = client.patch(
        f"/feiras/feira/{feira.id}/itens/{item_feira.id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"quantidade": 5}
    )
    assert resp.status_code == 403


def test_perfil_proprio_usuario(client: TestClient, usuario):
    token = get_token(client, usuario.email, "senha123")
    resp = client.get("/usuarios/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["id"] == usuario.id


def test_perfil_sem_autenticacao(client: TestClient):
    resp = client.get("/usuarios/me")
    assert resp.status_code == 401


def test_perfil_com_token_invalido(client: TestClient):
    resp = client.get("/usuarios/me", headers={"Authorization": "Bearer token_invalido"})
    assert resp.status_code == 401
