import pytest
from fastapi.testclient import TestClient


def get_token(client: TestClient, email: str, senha: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_criar_feira_sucesso(client: TestClient, usuario):
    token = get_token(client, usuario.email, "senha123")
    resp = client.post("/feiras/feira", headers={"Authorization": f"Bearer {token}"}, json={
        "nome": "Feira Semanal",
        "orcamento": 200.0
    })
    assert resp.status_code == 200
    assert resp.json()["message"] == "Feira criada com sucesso"


def test_criar_feira_duplicada(client: TestClient, usuario, feira):
    token = get_token(client, usuario.email, "senha123")
    resp = client.post("/feiras/feira", headers={"Authorization": f"Bearer {token}"}, json={
        "nome": feira.nome,
        "orcamento": 100.0
    })
    assert resp.status_code == 400
    assert "já existe" in resp.json()["detail"]


def test_criar_feira_com_feira_ativa(client: TestClient, usuario, feira):
    token = get_token(client, usuario.email, "senha123")
    resp = client.post("/feiras/feira", headers={"Authorization": f"Bearer {token}"}, json={
        "nome": "Nova Feira",
        "orcamento": 100.0
    })
    assert resp.status_code == 400
    assert "feira ativa" in resp.json()["detail"]


def test_listar_feiras_vazio(client: TestClient, usuario):
    token = get_token(client, usuario.email, "senha123")
    resp = client.get("/feiras/feira", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_listar_feiras_com_itens(client: TestClient, usuario, feira, item_feira):
    token = get_token(client, usuario.email, "senha123")
    resp = client.get("/feiras/feira", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_obter_feira_detalhe(client: TestClient, usuario, feira, item_feira):
    token = get_token(client, usuario.email, "senha123")
    resp = client.get(f"/feiras/feira/{feira.id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["id"] == feira.id
    assert len(resp.json()["itens"]) == 1


def test_atualizar_feira(client: TestClient, usuario, feira):
    token = get_token(client, usuario.email, "senha123")
    resp = client.put(f"/feiras/feira/{feira.id}", headers={"Authorization": f"Bearer {token}"}, json={
        "nome": "Feira Atualizada",
        "orcamento": 300.0
    })
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Feira Atualizada"
    assert resp.json()["orcamento"] == 300.0


def test_deletar_feira(client: TestClient, usuario, feira):
    token = get_token(client, usuario.email, "senha123")
    resp = client.delete(f"/feiras/feira/{feira.id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "sucesso" in resp.json()["message"]


def test_deletar_feira_idor_bloqueado(client: TestClient, usuario, usuario_admin):
    token = get_token(client, usuario_admin.email, "admin123")
    resp = client.delete(f"/feiras/feira/{usuario.id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_idor_acesso_feira_outro_usuario(client: TestClient, usuario, usuario_admin):
    # Cria feira para usuario
    token_u = get_token(client, usuario.email, "senha123")
    resp = client.post("/feiras/feira", headers={"Authorization": f"Bearer {token_u}"}, json={
        "nome": "Feira Privada",
        "orcamento": 100.0
    })
    assert resp.status_code == 200
    feiras = client.get("/feiras/feira", headers={"Authorization": f"Bearer {token_u}"}).json()
    feira_id = feiras[0]["id"]

    # Admin tenta acessar
    token_a = get_token(client, usuario_admin.email, "admin123")
    resp = client.get(f"/feiras/feira/{feira_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert resp.status_code == 403


def test_adicionar_item_feira(client: TestClient, usuario, feira):
    token = get_token(client, usuario.email, "senha123")
    resp = client.post(f"/feiras/feira/{feira.id}/itens", headers={"Authorization": f"Bearer {token}"}, json={
        "nome": "Arroz",
        "preco_varejo": 5.0,
        "quantidade": 2,
        "categoria": "Alimentos"
    })
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Arroz"


def test_listar_itens_feira(client: TestClient, usuario, feira, item_feira):
    token = get_token(client, usuario.email, "senha123")
    resp = client.get(f"/feiras/feira/{feira.id}/itens", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_atualizar_item_feira(client: TestClient, usuario, feira, item_feira):
    token = get_token(client, usuario.email, "senha123")
    resp = client.patch(
        f"/feiras/feira/{feira.id}/itens/{item_feira.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"quantidade": 5}
    )
    assert resp.status_code == 200
    assert resp.json()["quantidade"] == 5
    assert resp.json()["subtotal"] == 22.5


def test_deletar_item_feira(client: TestClient, usuario, feira, item_feira):
    token = get_token(client, usuario.email, "senha123")
    resp = client.delete(
        f"/feiras/feira/{feira.id}/itens/{item_feira.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert "sucesso" in resp.json()["message"]
