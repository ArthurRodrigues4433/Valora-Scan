import re
import io
import logging
from typing import Optional, Tuple
from paddleocr import PaddleOCR
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
from app.schemas.ocr import OCRResponse, ProdutoExtraido

logger = logging.getLogger(__name__)

ocr = PaddleOCR(
    lang="pt",
    use_angle_cls=True,
    show_log=False,
    rec=True,
    det=True,
)

PADROES_IGNORAR_NOME = [
    r"(?:PRECO|PREÇO|OFERTA|DESCONTO)",
    r"MIXMATEUS",
    r"(?:DATA|HORA):",
]

UNIDADES_MEDIDA = [
    (r"\d*\s*LITRO(S)?\b", "l"),
    (r"\d*\s*LT\b", "l"),
    (r"\b\d*\s*L\b", "l"),
    (r"\d*\s*KG\b", "kg"),
    (r"\d*\s*MG\b", "mg"),
    (r"\d*\s*ML\b", "ml"),
    (r"\d*\s*UN(ID)?(ADE)?S?\b", "un"),
    (r"\d*\s*UND\b", "un"),
    (r"\d*\s*UNID\b", "un"),
    (r"\d*\s*G\b", "g"),
]


def preprocessar_imagem(conteudo: bytes) -> np.ndarray:
    nparr = np.frombuffer(conteudo, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def extrair_codigos_barras(conteudo: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(conteudo))
        decodificados = decode(img)

        resultado = {
            "ean": None,
            "cod_interno": None,
            "codigos_raw": []
        }

        for codigo in decodificados:
            tipo = codigo.type
            valor = codigo.data.decode("utf-8").strip()
            resultado["codigos_raw"].append({"tipo": tipo, "valor": valor})

            if not resultado["ean"] and tipo in ("EAN13", "EAN8", "UPCA", "UPCE", "CODE128"):
                if len(valor) >= 8:
                    resultado["ean"] = valor

            if not resultado["cod_interno"] and tipo in ("CODE128", "CODE39", "ITF", "INTERLEAVED"):
                if valor:
                    resultado["cod_interno"] = valor

        return resultado
    except Exception as e:
        logger.warning(f"[CODIGO_BARRAS] Falha ao decodificar imagem: {e}")
        return {"ean": None, "cod_interno": None, "codigos_raw": []}


def extrair_cod_plu(texto: str) -> Optional[str]:
    padroes = [
        r"COD(?:IGO)?[\s:./]+PLU[\s:./]+([A-Z0-9\-]+)",
        r"PLU[\s:./]+([A-Z0-9\-]+)",
        r"COD(?:IGO)?[\s:./]+([A-Z0-9\-]+)",
        r"CÓD(?:IGO)?[\s:./]+([A-Z0-9\-]+)",
    ]

    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def extrair_ean_do_texto(texto: str) -> Optional[str]:
    linhas = texto.split("\n")
    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue
        candidato = linha_limpa.replace(" ", "").replace("-", "")
        if re.fullmatch(r"\d{8,14}", candidato):
            return candidato
    return None


def extrair_texto_ocr(conteudo: bytes) -> Tuple[str, float]:
    try:
        img = preprocessar_imagem(conteudo)
    except Exception as e:
        logger.warning(f"[OCR] Falha ao ler imagem: {e}")
        return "", 0.0

    if img is None:
        return "", 0.0

    try:
        resultados = ocr.ocr(img, cls=True)
    except Exception as e:
        logger.warning(f"[OCR] Falha no PaddleOCR: {e}")
        return "", 0.0

    textos = []
    confiancas = []

    if resultados and resultados[0] is not None:
        for linha in resultados[0]:
            texto = linha[1][0]
            confianca = linha[1][1]
            textos.append(texto)
            confiancas.append(confianca)

    texto_completo = "\n".join(textos)
    confianca_media = (sum(confiancas) / len(confiancas)) if confiancas else 0.0

    return texto_completo, confianca_media


def extrair_nome_produto(texto: str) -> Optional[str]:
    linhas = texto.split("\n")

    linhas_filtradas = []
    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue

        linha_upper = linha_limpa.upper()

        if re.search(r"^\d{8,}", linha_limpa):
            continue

        if re.search(r"^\d+[,.]\d+$", linha_limpa):
            continue

        if re.search(r"^(?:CO[O0]|COD|PLU|CÓD)", linha_upper):
            continue

        ignorar = False
        for padrao in PADROES_IGNORAR_NOME:
            if re.search(padrao, linha_upper, re.IGNORECASE):
                ignorar = True
                break

        if ignorar:
            continue

        linha_sem_preco = re.sub(r"(?:R\$\s*|\$)\s*\d+[,.]?\d{0,2}", "", linha_limpa).strip()
        linha_sem_preco = re.sub(r"\d+[,.]\d{2}", "", linha_sem_preco).strip()

        if linha_sem_preco and len(linha_sem_preco) > 2:
            linhas_filtradas.append(linha_sem_preco)

    if linhas_filtradas:
        return linhas_filtradas[0]

    return None


def normalizar_preco(valor: str) -> Optional[float]:
    if not valor:
        return None
    valor = valor.strip().replace(" ", "").replace("R$", "").replace("$", "")
    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    elif "." not in valor:
        valor = valor + ".00"
    try:
        return float(valor)
    except ValueError:
        return None


def extrair_precos(texto: str) -> list:
    precos_encontrados = []

    linhas = texto.split("\n")
    for linha in linhas:
        linha_limpa = linha.strip()
        linha_upper = linha_limpa.upper()

        if re.search(r"(?:CX|EMB|FARDO|LEVE|FD)\s*(\d+)", linha_upper):
            continue

        if re.search(r"PRECO\s*EQUIVALENTE|PREÇO\s*EQUIVALENTE|PRECOEQUIVALENTE|PREÇOEQUIVALENTE", linha_upper):
            continue

        if re.search(r"\bA\s+PARTIR\s+DE\s+\d+\b", linha_upper):
            continue

        if re.search(r"\d{2}/\d{2}/\d{2,4}(\s+\d{2}:\d{2})?", linha_limpa):
            continue

        if re.search(r"\b(SEU[_\-\s]?JORGE|JR|MEU[_\-\s]?ATACADO|ATACADO\s*DIA|DIA\s*DE|OFERTA|DESCONTO)\b", linha_upper):
            continue

        padrao_preco = r"(\d+[,.]\d{2})"
        matches = re.findall(padrao_preco, linha_limpa)

        for match in matches:
            preco = normalizar_preco(match)
            if preco is not None and preco not in precos_encontrados:
                precos_encontrados.append(preco)

    precos_encontrados.sort()

    return precos_encontrados


def extrair_qtd_atacado(texto: str) -> Optional[int]:
    padroes = [
        r"\bA\s*PARTIR\s*DE\s*(\d+)\s*UNI?D?S?\b",
        r"\bA\s*PARTIR\s*DE\s*(\d+)\b",
        r"CX\s*(\d+)\s*UNI?D?S?\b",
        r"CX\s*(\d+)\s+\b",
        r"EMB\s*(\d+)\s*UNI?D?S?\b",
        r"FARDO\s*(\d+)\s*UNI?D?S?\b",
        r"LEVE\s*(\d+)\s*UNI?D?S?\b",
    ]

    texto_upper = texto.upper()

    for padrao in padroes:
        match = re.search(padrao, texto_upper)
        if match:
            return int(match.group(1))

    return None


def extrair_unidade_medida(texto: str) -> Optional[str]:
    linhas = texto.split("\n")
    linhas_limpas = []
    for linha in linhas:
        linha_upper = linha.upper()
        if re.search(r"PRECO\s*EQUIVALENTE|PREÇO\s*EQUIVALENTE|PRECOEQUIVALENTE|PREÇOEQUIVALENTE", linha_upper):
            continue
        linhas_limpas.append(linha)

    texto_limpo = "\n".join(linhas_limpas)
    texto_upper = re.sub(r"\d+[,.]\d{2}", "", texto_limpo.upper())
    texto_upper = re.sub(r"(?:PRECO|PREÇO|OFERTA|DESCONTO|MIXMATEUS|DATA|HORA)", "", texto_upper, flags=re.IGNORECASE)

    for padrao, unidade in UNIDADES_MEDIDA:
        match = re.search(padrao, texto_upper)
        if match:
            return unidade
    return None


def parser_mix_mateus(texto: str, codigos_barras: dict) -> ProdutoExtraido:
    logger.debug("[MIXMATEUS] Processando texto específico do Mix Mateus")

    nome = extrair_nome_produto(texto)
    logger.debug(f"[MIXMATEUS] Nome encontrado: {nome}")

    precos = extrair_precos(texto)
    logger.debug(f"[MIXMATEUS] Preços encontrados: {precos}")

    preco_varejo = precos[1] if len(precos) >= 2 else (precos[0] if len(precos) >= 1 else None)
    preco_atacado = precos[0] if len(precos) >= 2 else None

    qtd_atacado = extrair_qtd_atacado(texto)
    logger.debug(f"[MIXMATEUS] Quantidade atacado encontrada: {qtd_atacado}")

    unidade = extrair_unidade_medida(texto)
    logger.debug(f"[MIXMATEUS] Unidade encontrada: {unidade}")

    cod_plu = extrair_cod_plu(texto)
    if not codigos_barras.get("cod_interno") and cod_plu:
        codigos_barras["cod_interno"] = cod_plu

    return ProdutoExtraido(
        nome=nome,
        preco_varejo=preco_varejo,
        preco_atacado=preco_atacado,
        qtd_minima_atacado=qtd_atacado,
        unidade_medida=unidade,
        ean=codigos_barras.get("ean"),
        cod_interno=codigos_barras.get("cod_interno"),
    )


def parser_assai(texto: str, codigos_barras: dict) -> ProdutoExtraido:
    logger.debug("[ASSAI] Processando texto específico do Assai")

    nome = extrair_nome_produto(texto)
    logger.debug(f"[ASSAI] Nome encontrado: {nome}")

    precos = extrair_precos(texto)
    logger.debug(f"[ASSAI] Preços encontrados: {precos}")

    preco_varejo = precos[1] if len(precos) >= 2 else (precos[0] if len(precos) >= 1 else None)
    preco_atacado = precos[0] if len(precos) >= 2 else None

    qtd_atacado = extrair_qtd_atacado(texto)
    logger.debug(f"[ASSAI] Quantidade atacado encontrada: {qtd_atacado}")

    unidade = extrair_unidade_medida(texto)
    logger.debug(f"[ASSAI] Unidade encontrada: {unidade}")

    cod_plu = extrair_cod_plu(texto)
    if not codigos_barras.get("cod_interno") and cod_plu:
        codigos_barras["cod_interno"] = cod_plu

    return ProdutoExtraido(
        nome=nome,
        preco_varejo=preco_varejo,
        preco_atacado=preco_atacado,
        qtd_minima_atacado=qtd_atacado,
        unidade_medida=unidade,
        ean=codigos_barras.get("ean"),
        cod_interno=codigos_barras.get("cod_interno"),
    )


def parser_atacadao(texto: str, codigos_barras: dict) -> ProdutoExtraido:
    logger.debug("[ATACADAO] Processando texto específico do Atacadao")

    nome = extrair_nome_produto(texto)
    logger.debug(f"[ATACADAO] Nome encontrado: {nome}")

    precos = extrair_precos(texto)
    logger.debug(f"[ATACADAO] Preços encontrados: {precos}")

    preco_varejo = precos[1] if len(precos) >= 2 else (precos[0] if len(precos) >= 1 else None)
    preco_atacado = precos[0] if len(precos) >= 2 else None

    qtd_atacado = extrair_qtd_atacado(texto)
    logger.debug(f"[ATACADAO] Quantidade atacado encontrada: {qtd_atacado}")

    unidade = extrair_unidade_medida(texto)
    logger.debug(f"[ATACADAO] Unidade encontrada: {unidade}")

    cod_plu = extrair_cod_plu(texto)
    if not codigos_barras.get("cod_interno") and cod_plu:
        codigos_barras["cod_interno"] = cod_plu

    return ProdutoExtraido(
        nome=nome,
        preco_varejo=preco_varejo,
        preco_atacado=preco_atacado,
        qtd_minima_atacado=qtd_atacado,
        unidade_medida=unidade,
        ean=codigos_barras.get("ean"),
        cod_interno=codigos_barras.get("cod_interno"),
    )


def detectar_supermercado(texto: str) -> str:
    texto_upper = texto.upper()

    if "MIXMATEUS" in texto_upper:
        return "mix_mateus"
    if "ASSAI" in texto_upper:
        return "assai"
    if "ATACADAO" in texto_upper:
        return "atacadao"

    return "generic"


def extrair_dados_produto(texto: str, codigos_barras: dict) -> ProdutoExtraido:
    supermercado = detectar_supermercado(texto)
    logger.debug(f"[OCR] Supermercado detectado: {supermercado}")

    if supermercado == "mix_mateus":
        return parser_mix_mateus(texto, codigos_barras)
    if supermercado == "assai":
        return parser_assai(texto, codigos_barras)
    if supermercado == "atacadao":
        return parser_atacadao(texto, codigos_barras)

    nome = extrair_nome_produto(texto)
    logger.debug(f"[OCR] Nome encontrado: {nome}")

    precos = extrair_precos(texto)
    logger.debug(f"[OCR] Preços encontrados: {precos}")

    preco_varejo = precos[1] if len(precos) >= 2 else (precos[0] if len(precos) >= 1 else None)
    preco_atacado = precos[0] if len(precos) >= 1 else None

    qtd_atacado = extrair_qtd_atacado(texto)
    logger.debug(f"[OCR] Quantidade atacado encontrada: {qtd_atacado}")

    unidade = extrair_unidade_medida(texto)
    logger.debug(f"[OCR] Unidade encontrada: {unidade}")

    cod_plu = extrair_cod_plu(texto)
    if not codigos_barras.get("cod_interno") and cod_plu:
        codigos_barras["cod_interno"] = cod_plu

    return ProdutoExtraido(
        nome=nome,
        preco_varejo=preco_varejo,
        preco_atacado=preco_atacado,
        qtd_minima_atacado=qtd_atacado,
        unidade_medida=unidade,
        ean=codigos_barras.get("ean"),
        cod_interno=codigos_barras.get("cod_interno"),
    )


async def processar_imagem_ocr(conteudo: bytes) -> OCRResponse:
    codigos_barras = extrair_codigos_barras(conteudo)
    logger.debug(f"[OCR] Códigos de barras detectados: {codigos_barras}")

    texto, confianca = extrair_texto_ocr(conteudo)
    logger.debug(f"[OCR DEBUG] Texto bruto: {texto}")
    logger.debug(f"[OCR DEBUG] Confiança: {confianca}")

    if not codigos_barras.get("ean"):
        ean_texto = extrair_ean_do_texto(texto)
        if ean_texto:
            codigos_barras["ean"] = ean_texto
            logger.debug(f"[OCR] EAN extraído do texto: {ean_texto}")

    produto = extrair_dados_produto(texto, codigos_barras)
    logger.debug(f"[OCR DEBUG] Produto extraído: {produto}")

    return OCRResponse(texto_extrato=texto, produto=produto, confianca=confianca)
