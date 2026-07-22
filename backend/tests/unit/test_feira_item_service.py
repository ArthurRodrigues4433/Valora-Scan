import pytest
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.feira_item_service import (
    calcular_preco_escolhido,
    calcular_preco_escolhido_from_floats,
    calcular_subtotal,
    criar_item,
    atualizar_item,
    deletar_item,
    recalcular_valor_previsto,
)
from app.schemas.feira_item import FeiraItemCreate, FeiraItemUpdate
from app.models.feira import Feira
from app.models.feira_item import FeiraItem


def test_calcular_preco_escolhido_varejo():
    result = calcular_preco_escolhido(
        quantidade=1, preco_varejo=Decimal("10.00"), preco_atacado=Decimal("8.00"), qtd_minima_atacado=5
    )
    assert float(result) == 10.0


def test_calcular_preco_escolhido_atacado():
    result = calcular_preco_escolhido(
        quantidade=5, preco_varejo=Decimal("10.00"), preco_atacado=Decimal("8.00"), qtd_minima_atacado=5
    )
    assert float(result) == 8.0


def test_calcular_preco_escolhido_sem_atacado():
    result = calcular_preco_escolhido(
        quantidade=5, preco_varejo=Decimal("10.00"), preco_atacado=Decimal("0.00"), qtd_minima_atacado=5
    )
    assert float(result) == 10.0


def test_calcular_preco_escolhido_atacado_zero():
    result = calcular_preco_escolhido(
        quantidade=10, preco_varejo=Decimal("5.00"), preco_atacado=Decimal("0.00"), qtd_minima_atacado=2
    )
    assert float(result) == 5.0


def test_calcular_preco_escolhido_from_floats():
    result = calcular_preco_escolhido_from_floats(3, 10.0, 8.5, 2)
    assert float(result) == 8.5


def test_calcular_subtotal():
    result = calcular_subtotal(quantidade=3, preco_escolhido=Decimal("4.50"))
    assert float(result) == 13.5


def test_calcular_subtotal_quantidade_zero():
    result = calcular_subtotal(quantidade=0, preco_escolhido=Decimal("10.00"))
    assert float(result) == 0.0


def test_criar_item_success(db_session: Session, feira: Feira):
    item_data = FeiraItemCreate(
        nome="Feijão",
        categoria="Alimentos",
        preco_varejo=8.0,
        preco_atacado=7.0,
        qtd_minima_atacado=3,
        quantidade=2,
        unidade_medida="kg",
        ean="7891111111111",
    )
    item = criar_item(feira_id=feira.id, item_data=item_data, session=db_session)
    assert item.id is not None
    assert item.nome == "Feijão"
    assert item.feira_id == feira.id
    assert item.subtotal == 16.0
    assert item.preco_escolhido == 8.0


def test_criar_item_sem_atacado_usar_varejo(db_session: Session, feira: Feira):
    db_session.rollback()
    item_data = FeiraItemCreate(
        nome="Arroz",
        categoria="Alimentos",
        preco_varejo=5.0,
        quantidade=1,
    )
    item = criar_item(feira_id=feira.id, item_data=item_data, session=db_session)
    assert item.preco_escolhido == 5.0
    assert item.subtotal == 5.0


def test_criar_item_feira_nao_encontrada(db_session: Session):
    item_data = FeiraItemCreate(nome="X", preco_varejo=1.0, quantidade=1)
    with pytest.raises(Exception):
        criar_item(feira_id=9999, item_data=item_data, session=db_session)


def test_criar_item_feira_finalizada_nao_permite(db_session: Session, feira: Feira):
    feira_obj = db_session.query(Feira).filter(Feira.id == feira.id).first()
    feira_obj.status = "finalizada"
    db_session.commit()
    item_data = FeiraItemCreate(nome="X", preco_varejo=1.0, quantidade=1)
    with pytest.raises(Exception):
        criar_item(feira_id=feira.id, item_data=item_data, session=db_session)


def test_atualizar_item_success(db_session: Session, item_feira: FeiraItem):
    update_data = FeiraItemUpdate(nome="Arroz Integral", quantidade=5)
    updated = atualizar_item(
        feira_id=item_feira.feira_id, item_id=item_feira.id, item_data=update_data, session=db_session
    )
    assert updated.nome == "Arroz Integral"
    assert updated.quantidade == 5
    assert updated.subtotal == 22.5


def test_atualizar_item_nao_encontrado(db_session: Session, feira: Feira):
    update_data = FeiraItemUpdate(nome="X")
    with pytest.raises(Exception):
        atualizar_item(feira_id=feira.id, item_id=9999, item_data=update_data, session=db_session)


def test_atualizar_item_recalcula_valor_previsto(db_session: Session, feira: Feira, item_feira: FeiraItem):
    feira_db = db_session.query(Feira).filter(Feira.id == feira.id).first()
    initial_total = feira_db.valor_previsto
    update_data = FeiraItemUpdate(preco_varejo=10.0)
    atualizar_item(feira_id=feira.id, item_id=item_feira.id, item_data=update_data, session=db_session)
    db_session.refresh(feira_db)
    assert feira_db.valor_previsto != initial_total


def test_deletar_item_success(db_session: Session, item_feira: FeiraItem):
    result = deletar_item(feira_id=item_feira.feira_id, item_id=item_feira.id, session=db_session)
    assert result["message"] == "Item deletado com sucesso"
    assert db_session.query(FeiraItem).filter(FeiraItem.id == item_feira.id).first() is None


def test_deletar_item_feira_finalizada_nao_permite(db_session: Session, feira: Feira, item_feira: FeiraItem):
    feira_obj = db_session.query(Feira).filter(Feira.id == feira.id).first()
    feira_obj.status = "finalizada"
    db_session.commit()
    with pytest.raises(Exception):
        deletar_item(feira_id=feira.id, item_id=item_feira.id, session=db_session)


def test_deletar_item_nao_encontrado(db_session: Session, feira: Feira):
    with pytest.raises(Exception):
        deletar_item(feira_id=feira.id, item_id=9999, session=db_session)


def test_recalcular_valor_previsto(db_session: Session, feira: Feira, item_feira: FeiraItem):
    feira_db = db_session.query(Feira).filter(Feira.id == feira.id).first()
    recalcular_valor_previsto(feira_id=feira.id, session=db_session)
    db_session.commit()
    db_session.refresh(feira_db)
    assert float(feira_db.valor_previsto) == float(item_feira.subtotal)
