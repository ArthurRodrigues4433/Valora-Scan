import pytest
import time
from fastapi.testclient import TestClient


def get_token(client: TestClient, email: str, senha: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_jwt_invalido_recusado(client: TestClient):
    resp = client.get("/usuarios/me", headers={"Authorization": "Bearer token.invalido.aqui"})
    assert resp.status_code == 401


def test_jwt_expirado_recusado(client: TestClient, usuario):
    import jwt
    from datetime import datetime, timedelta, timezone
    from app.services.auth_service import SECRET_KEY, ALGORITHM

    expired = {
        "sub": str(usuario.id),
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(seconds=10)
    }
    expired_token = jwt.encode(expired, SECRET_KEY, algorithm=ALGORITHM)
    resp = client.get("/usuarios/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401


def test_acesso_endpoint_protegido_sem_token(client: TestClient):
    resp = client.get("/feiras/feira")
    assert resp.status_code == 401

    resp = client.post("/feiras/feira", json={"nome": "X", "orcamento": 10})
    assert resp.status_code == 401

    resp = client.get("/nfce/divergencias/1")
    assert resp.status_code == 401


def test_idor_feira(client: TestClient, usuario):
    token = get_token(client, usuario.email, "senha123")
    resp = client.post("/feiras/feira", headers={"Authorization": f"Bearer {token}"}, json={
        "nome": "Feira IDOR",
        "orcamento": 50.0
    })
    assert resp.status_code == 200
    feiras = client.get("/feiras/feira", headers={"Authorization": f"Bearer {token}"}).json()
    feira_id = feiras[0]["id"]

    client.post("/auth/register", json={
        "nome": "Atacante",
        "email": "atacante@teste.com",
        "senha": "SenhaForte123"
    })
    token2 = get_token(client, "atacante@teste.com", "SenhaForte123")

    resp = client.get(f"/feiras/feira/{feira_id}", headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 403

    resp = client.put(f"/feiras/feira/{feira_id}", headers={"Authorization": f"Bearer {token2}"}, json={"nome": "Hackeado"})
    assert resp.status_code == 403

    resp = client.put(f"/feiras/feira/{feira_id}", headers={"Authorization": f"Bearer {token2}"}, json={"nome": "Hackeado"})
    assert resp.status_code == 403


def test_idor_item(client: TestClient, usuario, feira, item_feira):
    token = get_token(client, usuario.email, "senha123")

    client.post("/auth/register", json={
        "nome": "Atacante",
        "email": "atacante2@teste.com",
        "senha": "SenhaForte123"
    })
    token2 = get_token(client, "atacante2@teste.com", "SenhaForte123")

    resp = client.patch(
        f"/feiras/feira/{feira.id}/itens/{item_feira.id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"quantidade": 5}
    )
    assert resp.status_code == 403


def test_upload_arquivo_invalido(client: TestClient, usuario):
    token = get_token(client, usuario.email, "senha123")
    files = {"file": ("documento.pdf", b"%PDF-1.4 fake pdf content", "application/pdf")}
    resp = client.post("/ocr/etiqueta", headers={"Authorization": f"Bearer {token}"}, files=files)
    assert resp.status_code == 400
    assert "imagem" in resp.json()["detail"].lower()


def test_upload_arquivo_grande(client: TestClient, usuario):
    token = get_token(client, usuario.email, "senha123")
    big_content = b"x" * (6 * 1024 * 1024)
    files = {"file": ("grande.png", big_content, "image/png")}
    resp = client.post("/ocr/etiqueta", headers={"Authorization": f"Bearer {token}"}, files=files)
    assert resp.status_code == 413


def test_brute_force_rate_limit(client: TestClient, usuario):
    email = f"brute{int(time.time())}@teste.com"
    client.post("/auth/register", json={"nome": "BF", "email": email, "senha": "SenhaForte123"})

    for _ in range(5):
        client.post("/auth/login", json={"email": email, "senha": "errada"})

    resp = client.post("/auth/login", json={"email": email, "senha": "errada"})
    assert resp.status_code == 429 or resp.status_code == 401
