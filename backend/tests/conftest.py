import sys
import os
from pathlib import Path

# Garante que o diretório backend está no path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, pegar_session
from app.models.usuario import Usuario
from app.models.feira import Feira
from app.models.feira_item import FeiraItem
from app.models.nota_fiscal import NotaFiscal
from app.models.nota_fiscal_item import NotaFiscalItem
from app.services.auth_service import hash_password

# Engine de teste em memória
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_pegar_session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture(scope="function", autouse=True)
def reset_rate_limiter():
    try:
        from app.main import limiter
        limiter.reset()
    except Exception:
        pass
    yield
    try:
        from app.main import limiter
        limiter.reset()
    except Exception:
        pass


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    with TEST_ENGINE.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"DELETE FROM {table.name}"))
    yield


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[pegar_session] = override_pegar_session
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def db_session() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_session() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def usuario(test_session: Session) -> Usuario:
    usuario = Usuario(
        nome="Usuário Teste",
        email="teste@example.com",
        senha=hash_password("senha123"),
        ativo=True,
        admin=False,
    )
    test_session.add(usuario)
    test_session.commit()
    test_session.refresh(usuario)
    return usuario


@pytest.fixture(scope="function")
def usuario_admin(test_session: Session) -> Usuario:
    admin = Usuario(
        nome="Admin Teste",
        email="admin@example.com",
        senha=hash_password("admin123"),
        ativo=True,
        admin=True,
    )
    test_session.add(admin)
    test_session.commit()
    test_session.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def feira(test_session: Session, usuario: Usuario) -> Feira:
    feira = Feira(
        nome="Feira Teste",
        orcamento=100.00,
        valor_previsto=0.0,
        status="em_andamento",
        usuario_id=usuario.id,
    )
    test_session.add(feira)
    test_session.commit()
    test_session.refresh(feira)
    return feira


@pytest.fixture(scope="function")
def item_feira(test_session: Session, feira: Feira) -> FeiraItem:
    item = FeiraItem(
        nome="Arroz",
        categoria="Alimentos",
        preco_varejo=5.0,
        preco_atacado=4.5,
        qtd_minima_atacado=2,
        quantidade=1,
        preco_escolhido=5.0,
        subtotal=5.0,
        unidade_medida="kg",
        ean="7891234567890",
        feira_id=feira.id,
    )
    test_session.add(item)
    test_session.commit()
    test_session.refresh(item)
    return item


@pytest.fixture(scope="function")
def nota_fiscal(test_session: Session, feira: Feira) -> NotaFiscal:
    nota = NotaFiscal(
        mercado_nome="Supermercado Teste",
        valor_total=150.0,
        data_compra=__import__("datetime").datetime.utcnow(),
        qr_code="chave_teste",
        consentimento_lgpd=True,
        feira_id=feira.id,
    )
    test_session.add(nota)
    test_session.commit()
    test_session.refresh(nota)
    return nota


@pytest.fixture(scope="function")
def nota_fiscal_item(test_session: Session, nota_fiscal: NotaFiscal) -> NotaFiscalItem:
    item = NotaFiscalItem(
        produto_nome="Arroz",
        quantidade=2,
        preco_unitario=5.0,
        preco_total=10.0,
        divergencia=False,
        ean="7891234567890",
        nota_fiscal_id=nota_fiscal.id,
    )
    test_session.add(item)
    test_session.commit()
    test_session.refresh(item)
    return item
