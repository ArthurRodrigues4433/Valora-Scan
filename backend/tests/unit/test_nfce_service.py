import pytest
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

from app.services.nfce_service import NFCeService


def test_extrair_chave_com_parametro_p():
    qr = "https://site.com?p=12345678901234567890123456789012345678901234"
    chave = NFCeService.extrair_chave(qr)
    assert chave == "12345678901234567890123456789012345678901234"


def test_extrair_chave_string_44_caracteres():
    chave = "12345678901234567890123456789012345678901234"
    assert NFCeService.extrair_chave(chave) == chave


def test_extrair_chave_invalida_curta():
    with pytest.raises(ValueError):
        NFCeService.extrair_chave("abc123")


def test_extrair_chave_invalida_sem_parametro():
    with pytest.raises(ValueError):
        NFCeService.extrair_chave("https://site.com")


def test_consultar_nota_sucesso():
    xml_response = b"""<?xml version="1.0"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe><infNFe><ide><dhEmi>2024-01-01T10:00:00</dhEmi></ide></infNFe></NFe>
    </nfeProc>"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = xml_response
    mock_response.text = xml_response.decode()

    with patch("app.services.nfce_service.requests.get", return_value=mock_response):
        resultado = NFCeService.consultar_nota("12345678901234567890123456789012345678901234")

    assert "mercado_nome" in resultado
    assert "valor_total" in resultado
    assert "itens" in resultado


def test_consultar_nota_erro_http():
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("app.services.nfce_service.requests.get", return_value=mock_response):
        with pytest.raises(ValueError):
            NFCeService.consultar_nota("12345678901234567890123456789012345678901234")


def test_consultar_nota_xml_invalido():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"not xml"
    mock_response.text = "not xml"

    with patch("app.services.nfce_service.requests.get", return_value=mock_response):
        with pytest.raises(ValueError):
            NFCeService.consultar_nota("12345678901234567890123456789012345678901234")


def test_consultar_nota_erro_sefaz_100():
    xml_response = b"""<?xml version="1.0"?>
    <nfeProc>
        <erro>100</erro>
    </nfeProc>"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = xml_response
    mock_response.text = xml_response.decode()

    with patch("app.services.nfce_service.requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="Nota fiscal não encontrada"):
            NFCeService.consultar_nota("12345678901234567890123456789012345678901234")


def test_consultar_nota_erro_sefaz_101():
    xml_response = b"""<?xml version="1.0"?>
    <nfeProc>
        <erro>101</erro>
    </nfeProc>"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = xml_response
    mock_response.text = xml_response.decode()

    with patch("app.services.nfce_service.requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="cancelada"):
            NFCeService.consultar_nota("12345678901234567890123456789012345678901234")


def test_parse_xml_com_namespace():
    xml = b"""<?xml version="1.0"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe><infNFe>
            <ide><dhEmi>2024-01-01T10:00:00</dhEmi></ide>
            <emit><xNome>Mercado Teste</xNome></emit>
            <total><ICMSTot><vNF>150.00</vNF></ICMSTot></total>
            <det>
                <prod>
                    <xProd>Arroz</xProd>
                    <qCom>2</qCom>
                    <vUnCom>5.00</vUnCom>
                    <vProd>10.00</vProd>
                    <cProd>COD123</cProd>
                    <cEAN>7891234567890</cEAN>
                </prod>
            </det>
        </infNFe></NFe>
    </nfeProc>"""

    root = ET.fromstring(xml)
    resultado = NFCeService._parse_xml(root, xml.decode())

    assert resultado["mercado_nome"] == "Mercado Teste"
    assert resultado["valor_total"] == 150.0
    assert len(resultado["itens"]) == 1
    assert resultado["itens"][0]["produto_nome"] == "Arroz"
    assert resultado["itens"][0]["quantidade"] == 2
    assert resultado["itens"][0]["preco_unitario"] == 5.0
    assert resultado["itens"][0]["ean"] == "7891234567890"


def test_parse_xml_sem_namespace():
    xml = b"""<?xml version="1.0"?>
    <nfeProc>
        <NFe><infNFe>
            <ide><dhEmi>2024-01-01T10:00:00</dhEmi></ide>
            <emit><xNome>Mercado</xNome></emit>
            <total><ICMSTot><vNF>10.00</vNF></ICMSTot></total>
            <det>
                <prod>
                    <xProd>Feijao</xProd>
                    <qCom>1</qCom>
                    <vUnCom>10.00</vUnCom>
                    <vProd>10.00</vProd>
                    <cEAN>SEM GTIN</cEAN>
                </prod>
            </det>
        </infNFe></NFe>
    </nfeProc>"""

    root = ET.fromstring(xml)
    resultado = NFCeService._parse_xml(root, xml.decode())

    assert resultado["mercado_nome"] == "Mercado"
    assert resultado["itens"][0]["ean"] is None


def test_parse_xml_sem_itens():
    xml = b"""<?xml version="1.0"?>
    <nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
        <NFe><infNFe>
            <ide><dhEmi>2024-01-01T10:00:00</dhEmi></ide>
            <emit><xNome>Mercado</xNome></emit>
            <total><ICMSTot><vNF>0.00</vNF></ICMSTot></total>
        </infNFe></NFe>
    </nfeProc>"""

    root = ET.fromstring(xml)
    resultado = NFCeService._parse_xml(root, xml.decode())

    assert resultado["itens"] == []
    assert resultado["valor_total"] == 0.0
