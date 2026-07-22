import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

from app.services.ocr_service import (
    extrair_cod_plu,
    extrair_ean_do_texto,
    normalizar_preco,
    extrair_nome_produto,
    extrair_precos,
    extrair_qtd_atacado,
    extrair_unidade_medida,
    detectar_supermercado,
    parser_mix_mateus,
    parser_assai,
    parser_atacadao,
    extrair_dados_produto,
    _processar_imagem_ocr_sync,
)


def test_extrair_cod_plu_codigo_plu():
    texto = "CODIGO PLU 123ABC"
    assert extrair_cod_plu(texto) == "123ABC"


def test_extrair_cod_plu_plu_simples():
    texto = "PLU XYZ123"
    assert extrair_cod_plu(texto) == "XYZ123"


def test_extrair_cod_plu_codigo_simples():
    texto = "COD: 789"
    assert extrair_cod_plu(texto) == "789"


def test_extrair_cod_plu_sem_match():
    assert extrair_cod_plu("Produto generico") is None


def test_extrair_ean_do_texto_valido():
    texto = "7891234567890"
    assert extrair_ean_do_texto(texto) == "7891234567890"


def test_extrair_ean_do_texto_com_espacos():
    texto = "789 1234 567890"
    assert extrair_ean_do_texto(texto) == "7891234567890"


def test_extrair_ean_do_texto_sem_match():
    assert extrair_ean_do_texto("sem ean aqui") is None


def test_normalizar_preco_virgula():
    assert normalizar_preco("10,50") == 10.50


def test_normalizar_preco_ponto():
    assert normalizar_preco("10.50") == 10.50


def test_normalizar_preco_inteiro():
    assert normalizar_preco("10") == 10.0


def test_normalizar_preco_com_reais():
    assert normalizar_preco("R$ 10,50") == 10.50


def test_normalizar_preco_none():
    assert normalizar_preco(None) is None


def test_extrair_nome_produto_primeira_linha_valida():
    texto = "Arroz Branco\nPREÇO 5.00"
    assert extrair_nome_produto(texto) == "Arroz Branco"


def test_extrair_nome_produto_ignora_preco():
    texto = "5.00\nArroz"
    assert extrair_nome_produto(texto) == "Arroz"


def test_extrair_nome_produto_ignora_codigos():
    texto = "CODIGO 123\nArroz"
    assert extrair_nome_produto(texto) == "Arroz"


def test_extrair_nome_produto_ignora_mix_mateus():
    texto = "MIXMATEUS\nArroz"
    assert extrair_nome_produto(texto) == "Arroz"


def test_extrair_nome_produto_nenhum():
    assert extrair_nome_produto("PREÇO\nOFERTA\nDESCONTO") is None


def test_extrair_precos_basico():
    texto = "Arroz 5.00\nFeijao 7.50"
    precos = extrair_precos(texto)
    assert 5.0 in precos
    assert 7.5 in precos


def test_extrair_precos_remove_duplicatas():
    texto = "Arroz 5.00\nFeijao 5.00"
    precos = extrair_precos(texto)
    assert precos.count(5.0) == 1


def test_extrair_precos_ignora_embalagens():
    texto = "CX 10 5.00"
    precos = extrair_precos(texto)
    assert 5.0 not in precos


def test_extrair_qtd_atacado_a_partir_de():
    texto = "A PARTIR DE 6 UNIDADES"
    assert extrair_qtd_atacado(texto) == 6


def test_extrair_qtd_atacado_cx():
    texto = "CX 12 UNIDADES"
    assert extrair_qtd_atacado(texto) == 12


def test_extrair_qtd_atacado_sem_match():
    assert extrair_qtd_atacado("Produto normal") is None


def test_extrair_unidade_medida_kg():
    texto = "Arroz 1 KG"
    assert extrair_unidade_medida(texto) == "kg"


def test_extrair_unidade_medida_litro():
    texto = "Leite 1 LITRO"
    assert extrair_unidade_medida(texto) == "l"


def test_extrair_unidade_medida_sem_match():
    assert extrair_unidade_medida("Produto normal") is None


def test_detectar_supermercado_mix_mateus():
    assert detectar_supermercado("MIXMATEUS PROMOCAO") == "mix_mateus"


def test_detectar_supermercado_assai():
    assert detectar_supermercado("ASSAI ATACADISTA") == "assai"


def test_detectar_supermercado_atacadao():
    assert detectar_supermercado("ATACADAO") == "atacadao"


def test_detectar_supermercado_generico():
    assert detectar_supermercado("Supermercado generico") == "generic"


def test_parser_mix_mateus():
    texto = "MIXMATEUS\nArroz Branco 5KG\nPREÇO 25.90\n22.90\nA PARTIR DE 3 UN"
    codigos = {}
    resultado = parser_mix_mateus(texto, codigos)
    assert resultado.nome == "Arroz Branco 5KG"
    assert resultado.preco_varejo == 25.90
    assert resultado.preco_atacado == 22.90
    assert resultado.qtd_minima_atacado == 3


def test_parser_assai():
    texto = "Feijao Carioca 1KG\nPREÇO 8.90\n7.90\nA PARTIR DE 4 UN"
    codigos = {}
    resultado = parser_assai(texto, codigos)
    assert resultado.nome == "Feijao Carioca 1KG"
    assert resultado.preco_varejo == 8.90
    assert resultado.preco_atacado == 7.90


def test_parser_atacadao():
    texto = "Acucar 1KG\nPREÇO 4.50\n3.90\nA PARTIR DE 2 UN"
    codigos = {}
    resultado = parser_atacadao(texto, codigos)
    assert resultado.nome == "Acucar 1KG"
    assert resultado.preco_varejo == 4.50
    assert resultado.preco_atacado == 3.90


def test_extrair_dados_produto_generico():
    texto = "Arroz Branco 5KG\nPREÇO 25.90\nOFERTA 22.90"
    codigos = {}
    resultado = extrair_dados_produto(texto, codigos)
    assert resultado.nome == "Arroz Branco 5KG"
    assert resultado.preco_varejo == 25.90


def test_processar_imagem_ocr_sync_mock(monkeypatch):
    from app.schemas.ocr import ProdutoExtraido
    mock_codigos = {"ean": "7891234567890", "cod_interno": None, "codigos_raw": []}
    mock_produto = ProdutoExtraido(nome="Arroz", preco_varejo=5.0)
    mock_ocr_text = "Arroz\nPREÇO 5.00"

    monkeypatch.setattr("app.services.ocr_service.extrair_codigos_barras", lambda x: mock_codigos)
    monkeypatch.setattr("app.services.ocr_service.extrair_texto_ocr", lambda x: (mock_ocr_text, 0.9))
    monkeypatch.setattr("app.services.ocr_service.extrair_dados_produto", lambda t, c: mock_produto)

    resultado = _processar_imagem_ocr_sync(b"fake_image_bytes")
    assert resultado.texto_extrato == mock_ocr_text
    assert resultado.produto.nome == "Arroz"
    assert resultado.confianca == 0.9
