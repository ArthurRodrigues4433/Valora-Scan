import unicodedata
import re
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.models.feira_item import FeiraItem
from app.models.nota_fiscal import NotaFiscal
from app.models.nota_fiscal_item import NotaFiscalItem


class ComparadorService:

    @staticmethod
    def normalizar(texto: str) -> str:
        """Normaliza string para comparação"""
        if not texto:
            return ""

        # Remove acentos
        texto = unicodedata.normalize('NFD', texto)
        texto = texto.encode('ascii', 'ignore').decode('utf-8')

        # Lowercase e remove caracteres especiais
        texto = texto.lower()
        texto = re.sub(r'[^\w\s]', '', texto)

        # Remove unidades comuns
        unidades = ['kg', 'g', 'l', 'ml', 'un', 'und', 'pc', 'pct', 'cx', 'fd', 'lt']
        palavras = texto.split()
        palavras = [p for p in palavras if p not in unidades]

        return ' '.join(palavras)

    @staticmethod
    def calcular_similaridade(a: str, b: str) -> float:
        """Calcula similaridade entre duas strings (0 a 1)"""
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def comparar_feira_nota(feira_id: int, nota_fiscal_id: int, session: Session) -> dict:
        """
        Compara itens da feira (lista do usuário) com itens da nota fiscal
        """

        # Busca itens da feira
        itens_feira = session.query(FeiraItem).filter(
            FeiraItem.feira_id == feira_id
        ).all()

        # Busca itens da nota
        itens_nota = session.query(NotaFiscalItem).filter(
            NotaFiscalItem.nota_fiscal_id == nota_fiscal_id
        ).all()

        resultado = {
            "total_esperado": 0.0,
            "total_encontrado": 0.0,
            "total_divergencias": 0,
            "itens": [],
            "resumo": {
                "precos_maiores": [],
                "precos_menores": [],
                "nao_encontrados": [],
                "adicionais": []
            }
        }

        # Cria mapa normalizado dos itens da feira
        mapa_feira = {}
        for item in itens_feira:
            nome_norm = ComparadorService.normalizar(item.nome)
            mapa_feira[nome_norm] = item

        # Processa cada item da nota
        itens_nota_processados = set()

        for item_nota in itens_nota:
            nome_nota_norm = ComparadorService.normalizar(item_nota.produto_nome)

            # Tenta match exato primeiro
            match_exato = mapa_feira.get(nome_nota_norm)

            # Tenta fuzzy se não encontrou exato
            match_fuzzy = None
            if not match_exato:
                nomes_feira = list(mapa_feira.keys())
                if nomes_feira:
                    melhor_nome = None
                    melhor_score = 0.0
                    for nome_f in nomes_feira:
                        score = ComparadorService.calcular_similaridade(nome_nota_norm, nome_f)
                        if score > melhor_score:
                            melhor_score = score
                            melhor_nome = nome_f

                    if melhor_score >= 0.85 and melhor_nome is not None:
                        match_fuzzy = mapa_feira.get(melhor_nome)

            item_feira_match = match_exato or match_fuzzy

            if item_feira_match:
                # Item encontrado na lista
                valor_esperado = float(item_feira_match.preco_escolhido)
                valor_encontrado = float(item_nota.preco_unitario)
                diferenca = valor_encontrado - valor_esperado

                divergente = abs(diferenca) > 0.01  # Tolerância de 1 centavo

                if divergente:
                    item_nota.divergencia = True
                    item_nota.valor_esperado = Decimal(str(valor_esperado))
                    item_nota.diferenca = Decimal(str(diferenca))

                    if diferenca > 0:
                        resultado["resumo"]["precos_maiores"].append({
                            "nome": item_nota.produto_nome,
                            "esperado": valor_esperado,
                            "encontrado": valor_encontrado,
                            "diferenca": diferenca,
                            "item_feira_id": item_feira_match.id,
                            "item_nota_id": item_nota.id
                        })
                    else:
                        resultado["resumo"]["precos_menores"].append({
                            "nome": item_nota.produto_nome,
                            "esperado": valor_esperado,
                            "encontrado": valor_encontrado,
                            "diferenca": diferenca,
                            "item_feira_id": item_feira_match.id,
                            "item_nota_id": item_nota.id
                        })

                resultado["total_esperado"] += valor_esperado * item_nota.quantidade
                resultado["total_encontrado"] += valor_encontrado * item_nota.quantidade

                resultado["itens"].append({
                    "id": item_nota.id,
                    "nome": item_nota.produto_nome,
                    "nome_feira": item_feira_match.nome,
                    "quantidade": item_nota.quantidade,
                    "preco_esperado": valor_esperado,
                    "preco_encontrado": valor_encontrado,
                    "diferenca": diferenca,
                    "divergente": divergente,
                    "match_tipo": "exato" if match_exato else "fuzzy"
                })

                itens_nota_processados.add(item_nota.id)

            else:
                # Item na nota mas NÃO na lista
                item_nota.divergencia = True
                resultado["resumo"]["adicionais"].append({
                    "nome": item_nota.produto_nome,
                    "quantidade": item_nota.quantidade,
                    "preco": float(item_nota.preco_unitario),
                    "item_nota_id": item_nota.id
                })
                resultado["total_encontrado"] += float(item_nota.preco_total)

        # Verifica itens da feira que NÃO estão na nota
        itens_feira_ids = {i.id for i in itens_feira}
        itens_nota_feira_ids = {i.feira_item_id for i in itens_nota if i.feira_item_id}

        nao_encontrados = itens_feira_ids - itens_nota_feira_ids
        for item_feira in itens_feira:
            if item_feira.id in nao_encontrados:
                resultado["resumo"]["nao_encontrados"].append({
                    "nome": item_feira.nome,
                    "quantidade": item_feira.quantidade,
                    "preco": float(item_feira.preco_escolhido),
                    "item_feira_id": item_feira.id
                })
                resultado["total_esperado"] += float(item_feira.subtotal)

        resultado["total_divergencias"] = (
            len(resultado["resumo"]["precos_maiores"]) +
            len(resultado["resumo"]["precos_menores"]) +
            len(resultado["resumo"]["nao_encontrados"]) +
            len(resultado["resumo"]["adicionais"])
        )

        # Calcula economia/prejuízo
        economia = sum(abs(i["diferenca"]) for i in resultado["resumo"]["precos_menores"])
        prejuizo = sum(i["diferenca"] for i in resultado["resumo"]["precos_maiores"])
        resultado["economia"] = economia
        resultado["prejuizo"] = prejuizo if prejuizo > 0 else 0.0

        session.commit()

        return resultado
