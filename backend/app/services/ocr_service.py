import easyocr
import cv2
import numpy as np
from app.schemas.ocr import OCRResponse, ProdutoExtraido
import re

reader = easyocr.Reader(["pt"], gpu=False)


def preprocessar_imagem(conteudo: bytes) -> np.ndarray:
    """Converte bytes para imagem e aplica pré-processamento"""
    # Decodificar bytes para imagem
    nparr = np.frombuffer(conteudo, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Pré-processamento para melhorar OCR
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplicar threshold para binarizar
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh


def extrair_texto_ocr(conteudo: bytes) -> tuple[str, float]:
    """Extrai texto bruto da imagem usando EasyOCR"""
    img_processada = preprocessar_imagem(conteudo)

    # EasyOCR retorna lista de tuplas: [(bbox, texto, confianca), ...]
    resultados = reader.readtext(img_processada)

    # Extrair apenas textos e calcular confiança média
    textos = [texto for _, texto, _ in resultados]
    confiancas = [conf for _, _, conf in resultados]

    texto_completo = "\n".join(textos)
    confianca_media = sum(confiancas) / len(confiancas) if confiancas else 0.0

    return texto_completo, confianca_media


def extrair_precos_e_quantidade(texto: str) -> ProdutoExtraido:
    """Extrai preços varejo/atacado e quantidade mínima do texto OCR"""

    # Preços no formato R$ X,XX ou R$ X.XX
    precos = re.findall(r"R\$\s*(\d+[,.]\d{2})", texto)

    # Quantidade mínima - busca padrões como "a partir de 3 un", "3x und.", "mín 3 un"
    qtd_match = re.search(
        r"(?:a partir de|min|mínimo|\b)(?:\s*)(\d+)\s*(?:un|und|unid)",
        texto,
        re.IGNORECASE,
    )

    # Unidade de medida
    unid_match = re.search(
        r"\b(kg|pc|un|und|unid|g|ml|l|litro|lata)\b", texto, re.IGNORECASE
    )

    # Lógica: primeiro preço geralmente é varejo, segundo é atacado
    preco_varejo = float(precos[0].replace(",", ".")) if len(precos) >= 1 else None
    preco_atacado = float(precos[1].replace(",", ".")) if len(precos) >= 2 else None
    qtd_minima = int(qtd_match.group(1)) if qtd_match else None
    unidade = unid_match.group(1).lower() if unid_match else None

    return ProdutoExtraido(
        nome=None,
        preco_varejo=preco_varejo,
        preco_atacado=preco_atacado,
        qtd_minima_atacado=qtd_minima,
        unidade_medida=unidade,
    )


async def processar_imagem_ocr(conteudo: bytes) -> OCRResponse:
    """Função principal que processa imagem e retorna resposta completa"""
    texto, confianca = extrair_texto_ocr(conteudo)
    produto = extrair_precos_e_quantidade(texto)

    return OCRResponse(texto_extrato=texto, produto=produto, confianca=confianca)
