import pytest
from fastapi.testclient import TestClient

from tests.conftest import TestingSessionLocal
from app.models.usuario import Usuario
from app.services.auth_service import hash_password


def get_token(client: TestClient, email: str, senha: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_register_success(client: TestClient):
    resp = client.post("/auth/register", json={
        "nome": "Novo Usuário",
        "email": "novo@example.com",
        "senha": "SenhaForte123"
    })
    assert resp.status_code == 201
    assert resp.json()["message"] == "Usuário registrado com sucesso"


def test_register_duplicado(client: TestClient):
    client.post("/auth/register", json={
        "nome": "Usuário",
        "email": "dup@example.com",
        "senha": "SenhaForte123"
    })
    resp = client.post("/auth/register", json={
        "nome": "Usuário 2",
        "email": "dup@example.com",
        "senha": "SenhaForte123"
    })
    assert resp.status_code == 400
    assert "já existe" in resp.json()["detail"]


def test_login_success(client: TestClient, usuario):
    resp = client.post("/auth/login", json={"email": usuario.email, "senha": "senha123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert "refresh_token" in resp.json()


def test_login_credenciais_invalidas(client: TestClient, usuario):
    resp = client.post("/auth/login", json={"email": usuario.email, "senha": "errada"})
    assert resp.status_code == 401


def test_login_usuario_nao_encontrado(client: TestClient):
    resp = client.post("/auth/login", json={"email": "nope@example.com", "senha": "123"})
    assert resp.status_code == 401


def test_me_sucesso(client: TestClient, usuario):
    token = get_token(client, usuario.email, "senha123")
    resp = client.get("/usuarios/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == usuario.email


def test_me_sem_token(client: TestClient):
    resp = client.get("/usuarios/me")
    assert resp.status_code == 401


def test_me_token_invalido(client: TestClient):
    resp = client.get("/usuarios/me", headers={"Authorization": "Bearer token_invalido"})
    assert resp.status_code == 401


def test_refresh_token_sucesso(client: TestClient, usuario):
    login = client.post("/auth/login", json={"email": usuario.email, "senha": "senha123"}).json()
    refresh = login["refresh_token"]
    resp = client.get("/auth/refresh", headers={"Authorization": f"Bearer {refresh}"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_refresh_token_invalido(client: TestClient):
    resp = client.get("/auth/refresh", headers={"Authorization": "Bearer token_invalido"})
    assert resp.status_code == 401


def test_acesso_sem_autenticacao(client: TestClient):
    resp = client.get("/feiras/feira")
    assert resp.status_code == 401


def test_cadastro_senha_curta(client: TestClient):
    resp = client.post("/auth/register", json={
        "nome": "Usuario",
        "email": "curto@example.com",
        "senha": "123"
    })
    assert resp.status_code == 201


def test_login_form_success(client: TestClient, usuario):
    resp = client.post("/auth/login-form", data={"username": usuario.email, "password": "senha123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
