import pytest
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.comparador_service import ComparadorService
from app.models.feira import Feira
from app.models.feira_item import FeiraItem
from app.models.nota_fiscal import NotaFiscal
from app.models.nota_fiscal_item import NotaFiscalItem
from app.models.usuario import Usuario
from app.services.auth_service import hash_password


def test_normalizar_remove_acentos():
    texto = "Café Expresso"
    resultado = ComparadorService.normalizar(texto)
    assert "cafe" in resultado


def test_normalizar_lowercase():
    texto = "ARROZ BRANCO"
    resultado = ComparadorService.normalizar(texto)
    assert resultado == resultado.lower()


def test_normalizar_remove_pontuacao():
    texto = "Arroz, Feijão!"
    resultado = ComparadorService.normalizar(texto)
    assert "," not in resultado
    assert "!" not in resultado


def test_normalizar_remove_unidades():
    texto = "Arroz 1 kg"
    resultado = ComparadorService.normalizar(texto)
    assert "kg" not in resultado.split()


def test_normalizar_string_vazia():
    assert ComparadorService.normalizar("") == ""


def test_normalizar_none():
    assert ComparadorService.normalizar(None) == ""


def test_calcular_similaridade_igual():
    score = ComparadorService.calcular_similaridade("arroz branco", "arroz branco")
    assert score == 1.0


def test_calcular_similaridade_diferente():
    score = ComparadorService.calcular_similaridade("arroz", "feijao")
    assert score < 0.5


def test_calcular_similaridade_parcial():
    score = ComparadorService.calcular_similaridade("arroz integral", "arroz branco")
    assert 0 < score < 1


def test_calcular_similaridade_vazia():
    assert ComparadorService.calcular_similaridade("", "arroz") == 0.0
    assert ComparadorService.calcular_similaridade("arroz", "") == 0.0


def test_comparar_feira_nota_match_por_ean(db_session: Session):
    usuario = Usuario(nome="U", email="u@teste.com", senha="hash")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    feira = Feira(nome="F", orcamento=100, valor_previsto=0, status="em_andamento", usuario_id=usuario.id)
    db_session.add(feira)
    db_session.commit()
    db_session.refresh(feira)

    item_feira = FeiraItem(
        nome="Arroz",
        preco_varejo=Decimal("5.00"),
        preco_atacado=Decimal("4.50"),
        qtd_minima_atacado=2,
        quantidade=1,
        preco_escolhido=Decimal("5.00"),
        subtotal=Decimal("5.00"),
        ean="7891234567890",
        feira_id=feira.id,
    )
    db_session.add(item_feira)
    db_session.commit()
    db_session.refresh(item_feira)

    nota = NotaFiscal(
        mercado_nome="Mercado",
        valor_total=5.0,
        data_compra=__import__("datetime").datetime.utcnow(),
        qr_code="chave",
        consentimento_lgpd=True,
        feira_id=feira.id,
    )
    db_session.add(nota)
    db_session.commit()
    db_session.refresh(nota)

    item_nota = NotaFiscalItem(
        produto_nome="Arroz",
        quantidade=1,
        preco_unitario=Decimal("5.00"),
        preco_total=Decimal("5.00"),
        ean="7891234567890",
        nota_fiscal_id=nota.id,
    )
    db_session.add(item_nota)
    db_session.commit()
    db_session.refresh(item_nota)

    resultado = ComparadorService.comparar_feira_nota(feira.id, nota.id, db_session)
    assert len(resultado["itens"]) == 1
    assert resultado["itens"][0]["match_tipo"] == "ean"
    assert resultado["resumo"]["precos_maiores"] == []
    assert resultado["resumo"]["precos_menores"] == []
    assert resultado["total_divergencias"] == 0


def test_comparar_feira_nota_divergencia_preco(db_session: Session):
    usuario = Usuario(nome="U", email="u2@teste.com", senha="hash")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    feira = Feira(nome="F", orcamento=100, valor_previsto=0, status="em_andamento", usuario_id=usuario.id)
    db_session.add(feira)
    db_session.commit()
    db_session.refresh(feira)

    item_feira = FeiraItem(
        nome="Arroz",
        preco_varejo=Decimal("5.00"),
        preco_atacado=Decimal("4.50"),
        qtd_minima_atacado=2,
        quantidade=1,
        preco_escolhido=Decimal("5.00"),
        subtotal=Decimal("5.00"),
        ean="7891234567890",
        feira_id=feira.id,
    )
    db_session.add(item_feira)
    db_session.commit()
    db_session.refresh(item_feira)

    nota = NotaFiscal(
        mercado_nome="Mercado",
        valor_total=10.0,
        data_compra=__import__("datetime").datetime.utcnow(),
        qr_code="chave2",
        consentimento_lgpd=True,
        feira_id=feira.id,
    )
    db_session.add(nota)
    db_session.commit()
    db_session.refresh(nota)

    item_nota = NotaFiscalItem(
        produto_nome="Arroz",
        quantidade=2,
        preco_unitario=Decimal("6.00"),
        preco_total=Decimal("12.00"),
        ean="7891234567890",
        nota_fiscal_id=nota.id,
    )
    db_session.add(item_nota)
    db_session.commit()
    db_session.refresh(item_nota)

    resultado = ComparadorService.comparar_feira_nota(feira.id, nota.id, db_session)
    assert resultado["total_esperado"] == 10.0
    assert resultado["total_encontrado"] == 12.0
    assert resultado["total_divergencias"] == 1
    assert len(resultado["resumo"]["precos_maiores"]) == 1


def test_comparar_feira_nota_item_nao_encontrado(db_session: Session):
    usuario = Usuario(nome="U", email="u3@teste.com", senha="hash")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    feira = Feira(nome="F", orcamento=100, valor_previsto=0, status="em_andamento", usuario_id=usuario.id)
    db_session.add(feira)
    db_session.commit()
    db_session.refresh(feira)

    item_feira = FeiraItem(
        nome="Arroz",
        preco_varejo=Decimal("5.00"),
        preco_atacado=Decimal("4.50"),
        qtd_minima_atacado=2,
        quantidade=1,
        preco_escolhido=Decimal("5.00"),
        subtotal=Decimal("5.00"),
        ean="7891234567890",
        feira_id=feira.id,
    )
    db_session.add(item_feira)
    db_session.commit()
    db_session.refresh(item_feira)

    nota = NotaFiscal(
        mercado_nome="Mercado",
        valor_total=3.0,
        data_compra=__import__("datetime").datetime.utcnow(),
        qr_code="chave3",
        consentimento_lgpd=True,
        feira_id=feira.id,
    )
    db_session.add(nota)
    db_session.commit()
    db_session.refresh(nota)

    item_nota = NotaFiscalItem(
        produto_nome="Feijão",
        quantidade=1,
        preco_unitario=Decimal("3.00"),
        preco_total=Decimal("3.00"),
        ean="7890000000000",
        nota_fiscal_id=nota.id,
    )
    db_session.add(item_nota)
    db_session.commit()
    db_session.refresh(item_nota)

    resultado = ComparadorService.comparar_feira_nota(feira.id, nota.id, db_session)
    assert resultado["resumo"]["nao_encontrados"]
    assert resultado["resumo"]["adicionais"]
    assert resultado["total_divergencias"] == 2
