from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.dependencies.auth import verify_token
from app.core.database import pegar_session
from app.models.usuario import Usuario
from app.models.feira import Feira
from app.models.nota_fiscal import NotaFiscal
from app.models.nota_fiscal_item import NotaFiscalItem
from app.services.nfce_service import NFCeService
from app.services.comparador_service import ComparadorService
from datetime import datetime

nfce_router = APIRouter(prefix="/nfce", tags=["nfce"])


class NFCeRequest(BaseModel):
    feira_id: int
    qr_code: str
    consentimento_lgpd: bool = False


class NFCeResponse(BaseModel):
    nota_id: int
    feira_id: int
    mercado: str
    valor_total: float
    data_compra: str
    total_itens: int
    comparacao: dict


@nfce_router.post("/consultar", response_model=NFCeResponse)
async def consultar_nfce(
    request: NFCeRequest,
    session: Session = Depends(pegar_session),
    usuario: Usuario = Depends(verify_token)
):
    """
    Consulta NFCe na SEFAZ-PE e compara com a lista da feira.
    """

    if not request.consentimento_lgpd:
        raise HTTPException(400, "Você deve aceitar o consentimento LGPD para continuar")

    # 1. Valida feira
    feira = session.query(Feira).filter(
        Feira.id == request.feira_id,
        Feira.usuario_id == usuario.id
    ).first()

    if not feira:
        raise HTTPException(404, "Feira não encontrada")

    if feira.status == "finalizada":
        raise HTTPException(400, "Esta feira já foi finalizada")

    if not feira.feira_itens or len(feira.feira_itens) == 0:
        raise HTTPException(400, "Adicione produtos à feira antes de consultar a nota")

    # 2. Extrai chave de acesso para validar duplicidade
    try:
        chave = NFCeService.extrair_chave(request.qr_code)
    except ValueError as e:
        raise HTTPException(400, str(e))

    # 3. Verifica se nota já foi importada para esta feira
    nota_existente = session.query(NotaFiscal).filter(
        NotaFiscal.qr_code == chave,
        NotaFiscal.feira_id == request.feira_id
    ).first()

    if nota_existente:
        raise HTTPException(409, "Esta nota fiscal já foi importada para esta feira")

    # 4. Consulta SEFAZ-PE usando a URL completa do QR Code
    try:
        dados_nota = NFCeService.consultar_nota(request.qr_code)
    except ValueError as e:
        raise HTTPException(502, str(e))
    except Exception as e:
        raise HTTPException(502, f"Erro ao consultar SEFAZ: {str(e)}")

    # 5. Salva NotaFiscal
    nota = NotaFiscal(
        feira_id=request.feira_id,
        mercado_nome=dados_nota['mercado_nome'],
        valor_total=dados_nota['valor_total'],
        data_compra=dados_nota['data_compra'],
        qr_code=chave,
        consentimento_lgpd=True
    )
    session.add(nota)
    session.flush()

    # 6. Salva itens da nota
    for item_data in dados_nota['itens']:
        item_nota = NotaFiscalItem(
            nota_fiscal_id=nota.id,
            produto_nome=item_data['produto_nome'],
            quantidade=item_data['quantidade'],
            preco_unitario=item_data['preco_unitario'],
            preco_total=item_data['preco_total'],
            divergencia=False,
            valor_esperado=None,
            diferenca=None,
            ean=item_data.get('ean'),
            cprod=item_data.get('cprod'),
            ncm=item_data.get('ncm')
        )
        session.add(item_nota)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Esta nota fiscal já foi importada para esta feira")

    # 7. Executa comparação
    comparacao = ComparadorService.comparar_feira_nota(request.feira_id, nota.id, session)

    return {
        "nota_id": nota.id,
        "feira_id": request.feira_id,
        "mercado": nota.mercado_nome,
        "valor_total": float(nota.valor_total),
        "data_compra": nota.data_compra.isoformat(),
        "total_itens": len(dados_nota['itens']),
        "comparacao": comparacao
    }


@nfce_router.get("/divergencias/{feira_id}")
async def listar_divergencias(
    feira_id: int,
    session: Session = Depends(pegar_session),
    usuario: Usuario = Depends(verify_token)
):
    """Lista divergências de uma feira"""

    feira = session.query(Feira).filter(
        Feira.id == feira_id,
        Feira.usuario_id == usuario.id
    ).first()

    if not feira:
        raise HTTPException(404, "Feira não encontrada")

    # Busca todas as notas da feira
    notas = session.query(NotaFiscal).filter(
        NotaFiscal.feira_id == feira_id
    ).all()

    todas_divergencias = []
    for nota in notas:
        itens_divergentes = session.query(NotaFiscalItem).filter(
            NotaFiscalItem.nota_fiscal_id == nota.id,
            NotaFiscalItem.divergencia == True
        ).all()

        for item in itens_divergentes:
            tipo = "preco_maior"
            if item.diferenca is not None and item.diferenca < 0:
                tipo = "preco_menor"

            todas_divergencias.append({
                "nota_id": nota.id,
                "mercado": nota.mercado_nome,
                "produto": item.produto_nome,
                "quantidade": item.quantidade,
                "preco_esperado": float(item.valor_esperado) if item.valor_esperado else 0,
                "preco_encontrado": float(item.preco_unitario),
                "diferenca": float(item.diferenca) if item.diferenca else 0,
                "tipo": tipo
            })

    return {
        "feira_id": feira_id,
        "total_divergencias": len(todas_divergencias),
        "divergencias": todas_divergencias
    }
