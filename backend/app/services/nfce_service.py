import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional
import re
import logging


logger = logging.getLogger(__name__)


class NFCeService:

    BASE_URL = "https://nfce.sefaz.pe.gov.br:444/nfce-web/consultarNFCe"

    @staticmethod
    def extrair_chave(qr_data: str) -> str:
        """Extrai chave de acesso de QR Code ou URL"""

        match = re.search(r'[?&]p=([0-9A-Za-z]{44})', qr_data)
        if match:
            return match.group(1)

        if re.match(r'^[0-9A-Za-z]{44}$', qr_data.strip()):
            return qr_data.strip()

        raise ValueError("QR Code inválido: não foi possível extrair a chave de acesso")

    @staticmethod
    def consultar_nota(qr_data: str) -> dict:
        """Consulta NFCe na SEFAZ-PE e retorna dados estruturados"""

        chave = NFCeService.extrair_chave(qr_data)
        url = f"{NFCeService.BASE_URL}?p={chave}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/xml,text/xml,*/*",
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            raise ValueError(f"Erro ao consultar SEFAZ: HTTP {response.status_code}")

        # Parse do XML
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            raise ValueError("Erro ao processar resposta da SEFAZ")

        # Verifica se houve erro
        erro_elem = root.find('.//erro')
        if erro_elem is not None and erro_elem.text and erro_elem.text.strip() not in ('0', ''):
            codigo_erro = erro_elem.text.strip()
            if codigo_erro == '100':
                raise ValueError("Nota fiscal não encontrada ou chave inválida")
            elif codigo_erro == '101':
                raise ValueError("Nota fiscal cancelada")
            else:
                raise ValueError(f"Erro na consulta: código {codigo_erro}")

        # Extrai dados da nota
        return NFCeService._parse_xml(root, response.text)

    @staticmethod
    def _parse_xml(root: ET.Element, raw_xml: str = "") -> dict:
        """Extrai dados do XML da NFCe - tenta múltiplas estruturas"""

        nota = {}

        # Tenta diferentes namespaces
        namespaces = [
            {'nfe': 'http://www.portalfiscal.inf.br/nfe'},
            {'nfe': 'http://www.portalfiscal.inf.br/nfe/'},
            {},
        ]

        # Tenta encontrar mercado com diferentes namespaces
        mercado_nome = None
        for ns in namespaces:
            if ns:
                emit_xnome = root.find('.//nfe:emit/nfe:xNome', ns)
            else:
                emit_xnome = root.find('.//emit/xNome')
            if emit_xnome is not None and emit_xnome.text:
                mercado_nome = emit_xnome.text
                break

        nota['mercado_nome'] = mercado_nome or "Supermercado"

        # Tenta encontrar valor total
        valor_total = None
        for ns in namespaces:
            if ns:
                vnf = root.find('.//nfe:total/nfe:ICMSTot/nfe:vNF', ns)
            else:
                vnf = root.find('.//total/ICMSTot/vNF')
            if vnf is not None and vnf.text:
                try:
                    valor_total = float(vnf.text)
                    break
                except:
                    pass

        nota['valor_total'] = valor_total or 0.0

        # Tenta encontrar data de emissão
        data_compra = None
        for ns in namespaces:
            if ns:
                dhemi = root.find('.//nfe:ide/nfe:dhEmi', ns)
            else:
                dhemi = root.find('.//ide/dhEmi')
            if dhemi is not None and dhemi.text:
                try:
                    texto = dhemi.text.strip()
                    if len(texto) >= 19:
                        data_compra = datetime.strptime(texto[:19], "%Y-%m-%dT%H:%M:%S")
                    break
                except:
                    pass

        nota['data_compra'] = data_compra or datetime.utcnow()

        # Tenta encontrar itens com diferentes namespaces
        itens = []
        for ns in namespaces:
            if ns:
                det_list = root.findall('.//nfe:det', ns)
            else:
                det_list = root.findall('.//det')
            if det_list:
                for det in det_list:
                    item = {}

                    # Nome do produto
                    if ns:
                        xprod = det.find('nfe:prod/nfe:xProd', ns)
                    else:
                        xprod = det.find('prod/xProd')
                    item['produto_nome'] = xprod.text if xprod is not None else "Produto"

                    # Quantidade
                    if ns:
                        qcom = det.find('nfe:prod/nfe:qCom', ns)
                    else:
                        qcom = det.find('prod/qCom')
                    if qcom is not None and qcom.text:
                        try:
                            item['quantidade'] = int(float(qcom.text))
                        except:
                            item['quantidade'] = 1
                    else:
                        item['quantidade'] = 1

                    # Preço unitário
                    if ns:
                        vuncom = det.find('nfe:prod/nfe:vUnCom', ns)
                    else:
                        vuncom = det.find('prod/vUnCom')
                    item['preco_unitario'] = float(vuncom.text) if vuncom is not None and vuncom.text else 0.0

                    # Preço total
                    if ns:
                        vprod = det.find('nfe:prod/nfe:vProd', ns)
                    else:
                        vprod = det.find('prod/vProd')
                    item['preco_total'] = float(vprod.text) if vprod is not None and vprod.text else 0.0

                    # Código interno do produto (cProd)
                    if ns:
                        cprod = det.find('nfe:prod/nfe:cProd', ns)
                    else:
                        cprod = det.find('prod/cProd')
                    item['cprod'] = cprod.text.strip() if cprod is not None and cprod.text else None

                    # EAN/GTIN (cEAN)
                    if ns:
                        c_ean = det.find('nfe:prod/nfe:cEAN', ns)
                    else:
                        c_ean = det.find('prod/cEAN')
                    ean = c_ean.text.strip() if c_ean is not None and c_ean.text else None
                    if not ean or ean.upper() in ('SEM GTIN', '00000000000000'):
                        ean = None
                    item['ean'] = ean

                    # EAN tributável (cEANTrib)
                    if ns:
                        c_ean_trib = det.find('nfe:prod/nfe:cEANTrib', ns)
                    else:
                        c_ean_trib = det.find('prod/cEANTrib')
                    ean_trib = c_ean_trib.text.strip() if c_ean_trib is not None and c_ean_trib.text else None
                    if not ean_trib or ean_trib.upper() in ('SEM GTIN', '00000000000000'):
                        ean_trib = None
                    if not item['ean'] and ean_trib:
                        item['ean'] = ean_trib

                    # NCM
                    if ns:
                        ncm = det.find('nfe:prod/nfe:NCM', ns)
                    else:
                        ncm = det.find('prod/NCM')
                    ncm_val = ncm.text.strip() if ncm is not None and ncm.text else None
                    if ncm_val and ncm_val.lower() != 'none':
                        item['ncm'] = ncm_val
                    else:
                        item['ncm'] = None

                    itens.append(item)
                break

        nota['itens'] = itens

        if not mercado_nome or not valor_total or not itens:
            logger.warning(
                "[NFCe] XML parsing incomplete - mercado=%s, valor_total=%s, itens=%s",
                mercado_nome, valor_total, len(itens)
            )

        return nota
