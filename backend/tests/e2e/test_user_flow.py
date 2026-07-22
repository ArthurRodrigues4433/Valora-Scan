import pytest
from fastapi.testclient import TestClient


def get_token(client: TestClient, email: str, senha: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_fluxo_completo_usuario(client: TestClient):
    email = f"e2e_{int(__import__('time').time())}@teste.com"
    senha = "SenhaForte123"

    # 1. Cadastro
    resp = client.post("/auth/register", json={
        "nome": "Usuário E2E",
        "email": email,
        "senha": senha
    })
    assert resp.status_code == 201

    # 2. Login
    token = get_token(client, email, senha)
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Criar feira
    resp = client.post("/feiras/feira", headers=headers, json={
        "nome": "Feira E2E",
        "orcamento": 150.0
    })
    assert resp.status_code == 200
    feiras = client.get("/feiras/feira", headers=headers).json()
    feira_id = feiras[0]["id"]

    # 4. Adicionar item
    resp = client.post(f"/feiras/feira/{feira_id}/itens", headers=headers, json={
        "nome": "Arroz",
        "preco_varejo": 5.0,
        "quantidade": 2,
        "categoria": "Alimentos"
    })
    assert resp.status_code == 200
    item_id = resp.json()["id"]

    # 5. Consultar NFCe (mock IDOR validation will skip external HTTP)
    # Aqui apenas validamos que o endpoint exige feira ativa e consentimento
    resp = client.post("/nfce/consultar", headers=headers, json={
        "feira_id": feira_id,
        "qr_code": "123456789012345678901234567890123456789012",
        "consentimento_lgpd": False
    })
    assert resp.status_code == 400

    # 6. Validar listagem de itens
    resp = client.get(f"/feiras/feira/{feira_id}/itens", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["nome"] == "Arroz"

    # 7. Atualizar item
    resp = client.patch(
        f"/feiras/feira/{feira_id}/itens/{item_id}",
        headers=headers,
        json={"quantidade": 5}
    )
    assert resp.status_code == 200
    assert resp.json()["quantidade"] == 5
    assert resp.json()["subtotal"] == 25.0

    # 8. Verificar perfil
    resp = client.get("/usuarios/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == email
