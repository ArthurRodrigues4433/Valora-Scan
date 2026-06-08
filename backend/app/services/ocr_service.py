from paddleocr import PaddleOCR
import cv2
import numpy as np
from app.schemas.ocr import OCRResponse, ProdutoExtraido
import re

ocr = PaddleOCR(
    lang="pt",
    use_angle_cls=True,
    show_log=False,
    rec=True,
    det=True,
)


def preprocessar_imagem(conteudo: bytes) -> np.ndarray:
    """Converte bytes para imagem"""
    nparr = np.frombuffer(conteudo, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def extrair_texto_ocr(conteudo: bytes) -> tuple[str, float]:
    """Extrai texto bruto da imagem usando PaddleOCR"""
    img = preprocessar_imagem(conteudo)
    
    resultados = ocr.ocr(img, cls=True)
    
    textos = []
    confiancas = []
    
    if resultados and resultados[0] is not None:
        for linha in resultados[0]:
            texto = linha[1][0]
            confianca = linha[1][1]
            textos.append(texto)
            confiancas.append(confianca)
    
    texto_completo = "\n".join(textos)
    confianca_media = sum(confiancas) / len(confiancas) if confiancas else 0.0
    
    return texto_completo, confianca_media


def extrair_nome_produto(texto: str) -> str | None:
    linhas = texto.split("\n")

    padroes_ignorar = [
        r"R\$\s*\d+[,.]\d{2}",  # Preços
        r"(?:a partir de|min|mínimo|\b)(?:\s*)(\d+)\s*(?:un|und|unid)",
        r"(?:kg|g|ml|l|litro|lata|pc|un|und|unid)\b",
        r"(?:preço|varejo|atacado|valor)",
        r"(?:promo|oferta|desconto)",
        r"^\s*$",
        r"^\d+\s*$", 
    ]

    linhas_filtradas = []
    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue

        if not any(re.search(p, linha_limpa, re.IGNORECASE) for p in padroes_ignorar):
            # Remove acoláculos de preços da linha
            linha_sem_preco = re.sub(r"R\$\s*\d+[,.]\d{2}", "", linha_limpa).strip()
            if linha_sem_preco:
                linhas_filtradas.append(linha_sem_preco)

    # Retorna a(s) linha(s) mais relevante(s) como nome
    if linhas_filtradas:
        # Prioriza linhas mais longas (provavelmente o nome)
        linhas_filtradas.sort(key=len, reverse=True)
        return linhas_filtradas[0] if linhas_filtradas[0] else None

    return None

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

    nome = extrair_nome_produto(texto)

    return ProdutoExtraido(
        nome=nome,
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
