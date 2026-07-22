from sqlalchemy.orm import Session
from app.models.feira_item import FeiraItem
from app.models.feira import Feira
from app.schemas.feira_item import FeiraItemCreate, FeiraItemUpdate
from fastapi import HTTPException
from decimal import Decimal
from sqlalchemy import func


def calcular_preco_escolhido(quantidade: int, preco_varejo: Decimal, preco_atacado: Decimal, qtd_minima_atacado: int) -> float:
    """
    Calcula o preço escolhido com base na quantidade e nos preços de varejo e atacado.
    Se a quantidade for maior ou igual à quantidade mínima para atacado, retorna o preço de atacado, caso contrário, retorna o preço de varejo.
    Se preco_atacado for 0 ou None, usa sempre o varejo.
    """
    if float(preco_atacado) > 0 and quantidade >= qtd_minima_atacado:
        return float(preco_atacado)
    return float(preco_varejo)


def calcular_preco_escolhido_from_floats(quantidade: int, preco_varejo: float, preco_atacado: float, qtd_minima_atacado: int) -> float:
    """Wrapper para calcular_preco_escolhido com floats."""
    return calcular_preco_escolhido(quantidade, Decimal(str(preco_varejo)), Decimal(str(preco_atacado)), qtd_minima_atacado)


def calcular_subtotal(quantidade: int, preco_escolhido: Decimal) -> float:
    """
    Calcula o subtotal do item com base na quantidade e no preço escolhido.
    """
    return float(quantidade * preco_escolhido)


def criar_item(feira_id: int, item_data: FeiraItemCreate, session: Session) -> FeiraItem:

    feira = session.query(Feira).filter(Feira.id == feira_id).first()
    if not feira:
        raise HTTPException(status_code=404, detail="Feira não encontrada")

    if feira.status == "finalizada":
        raise HTTPException(
            status_code=400, detail="Feira já finalizada, não pode ser editada"
        )

    preco_atacado = item_data.preco_atacado if item_data.preco_atacado is not None else Decimal("0")
    qtd_minima = item_data.qtd_minima_atacado if item_data.qtd_minima_atacado is not None else None

    # Se não houver preço de atacado ou quantidade mínima, força varejo
    if not preco_atacado or not qtd_minima:
        preco_escolhido = float(item_data.preco_varejo)
    else:
        preco_escolhido = calcular_preco_escolhido(
            item_data.quantidade,
            Decimal(str(item_data.preco_varejo)),
            preco_atacado,
            qtd_minima,
        )

    subtotal = calcular_subtotal(item_data.quantidade, Decimal(preco_escolhido))

    novo_item = FeiraItem(
        nome=item_data.nome,
        categoria=item_data.categoria,
        preco_varejo=Decimal(str(item_data.preco_varejo)),
        preco_atacado=preco_atacado,
        qtd_minima_atacado=qtd_minima or 1,
        quantidade=item_data.quantidade,
        preco_escolhido=preco_escolhido,
        subtotal=subtotal,
        unidade_medida=item_data.unidade_medida or "",
        imagem_url=item_data.imagem_url,
        ocr_texto=item_data.ocr_texto,
        ean=item_data.ean,
        cod_interno=item_data.cod_interno,
        feira_id=feira_id,
    )
    
    session.add(novo_item)
    session.commit()
    session.refresh(novo_item)

    recalcular_valor_previsto(feira_id, session)

    return novo_item


def atualizar_item(feira_id: int, item_id: int, item_data: FeiraItemUpdate, session: Session) -> FeiraItem:
    """
    Atualiza um item da feira. Permite atualizar qualquer campo do item, e se os preços ou quantidade forem alterados, recalcula o preço escolhido, subtotal e valor previsto da feira.
    1. Valida se o item existe e pertence à feira
    2. Valida se a feira NÃO está finalizada
    3. Atualiza os campos do item
    4. Recalcula preco_escolhido e subtotal se necessário
    5. Recalcula valor_previsto da feira
    """

    feira = session.query(Feira).filter(Feira.id == feira_id).first()
    if not feira:
        raise HTTPException(status_code=404, detail="Feira não encontrada")

    if feira.status == "finalizada":
        raise HTTPException(
            status_code=400, detail="Feira já finalizada, não pode ser editada"
        )

    item = (
        session.query(FeiraItem)
        .filter(FeiraItem.id == item_id, FeiraItem.feira_id == feira_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    if item_data.nome is not None:
        item.nome = item_data.nome
    if item_data.categoria is not None:
        item.categoria = item_data.categoria
    if item_data.unidade_medida is not None:
        item.unidade_medida = item_data.unidade_medida
    if item_data.imagem_url is not None:
        item.imagem_url = item_data.imagem_url
    if item_data.ocr_texto is not None:
        item.ocr_texto = item_data.ocr_texto
    if item_data.ean is not None:
        item.ean = item_data.ean
    if item_data.cod_interno is not None:
        item.cod_interno = item_data.cod_interno

    # Se algum preço mudou, recalcula preco_escolhido e subtotal
    preco_varejo = float(
        item_data.preco_varejo
        if item_data.preco_varejo is not None
        else item.preco_varejo
    )
    preco_atacado_val = float(
        item_data.preco_atacado
        if item_data.preco_atacado is not None
        else item.preco_atacado or 0
    )
    qtd_minima_atacado_val = (
        item_data.qtd_minima_atacado
        if item_data.qtd_minima_atacado is not None
        else item.qtd_minima_atacado or 1
    )
    quantidade = (
        item_data.quantidade if item_data.quantidade is not None else item.quantidade
    )

    if not preco_atacado_val or not qtd_minima_atacado_val:
        preco_escolhido = preco_varejo
    else:
        preco_escolhido = calcular_preco_escolhido_from_floats(
            quantidade, preco_varejo, preco_atacado_val, qtd_minima_atacado_val
        )

    item.preco_varejo = Decimal(str(preco_varejo))
    item.preco_atacado = Decimal(str(preco_atacado_val))
    item.qtd_minima_atacado = qtd_minima_atacado_val or 1
    item.quantidade = quantidade
    item.preco_escolhido = preco_escolhido
    item.subtotal = calcular_subtotal(quantidade, Decimal(str(preco_escolhido)))

    session.commit()
    session.refresh(item)

    # Recalcula valor_previsto da feira
    recalcular_valor_previsto(feira_id, session)

    return item


def deletar_item(feira_id: int, item_id: int, session: Session) -> dict:
    """
    1. Valida se o item existe e pertence à feira
    2. Valida se a feira NÃO está finalizada
    3. Deleta o item
    4. Recalcula valor_previsto da feira
    """
    # Verifica se a feira existe
    feira = session.query(Feira).filter(Feira.id == feira_id).first()
    if not feira:
        raise HTTPException(status_code=404, detail="Feira não encontrada")

    # Bloqueia deleção em feiras finalizadas
    if feira.status == "finalizada":
        raise HTTPException(
            status_code=400,
            detail="Não é possível deletar itens em uma feira finalizada",
        )

    # Verifica se o item existe e pertence à feira
    item = (
        session.query(FeiraItem)
        .filter(FeiraItem.id == item_id, FeiraItem.feira_id == feira_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    session.delete(item)
    session.commit()

    # Recalcula valor_previsto da feira
    recalcular_valor_previsto(feira_id, session)

    return {"message": "Item deletado com sucesso"}


def recalcular_valor_previsto(feira_id: int, session: Session) -> None:
    """
    Soma todos os subtotais dos itens da feira e atualiza Feira.valor_previsto
    """
    feira = session.query(Feira).filter(Feira.id == feira_id).first()
    if not feira:
        raise HTTPException(status_code=404, detail="Feira não encontrada")

    # Soma todos os subtotais
    total = (
        session.query(FeiraItem)
        .filter(FeiraItem.feira_id == feira_id)
        .with_entities(func.sum(FeiraItem.subtotal))
        .scalar()
    )

    # Se não há itens, total é None; convertemos para 0
    feira.valor_previsto = total if total else 0

    session.commit()
    session.refresh(feira)