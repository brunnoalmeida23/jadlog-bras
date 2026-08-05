# app/services/frete_calculator.py
"""
CALCULADORA DE FRETE JADLOG BRÁS
REGRAS:
1. GLM = Preço base (tabela Capital/Interior)
2. LUCRO = Margem do revendedor (planilha "final clientes impressão")
3. PREÇO FINAL = GLM + LUCRO (valor que o cliente final paga)
4. AD VALOREM = 0,66% da NF (se NF > R$ 100)
5. TOTAL = PREÇO FINAL + AD VALOREM
"""

from .cep_service import CEPService


class FreteCalculator:
    def __init__(self):
        self.cep_service = CEPService()
        self.tabelas = self._carregar_tabelas()
        self.lucros = self._carregar_lucros()

    def _carregar_tabelas(self):
        """Tabelas GLM (Capital 1,2,3 / Interior 1,2,3)"""
        return {
            "capital_1": {
                "PACKAGE": {1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99, "adicional": 0.9072},
                ".COM": {1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99, "adicional": 0.9072}
            },
            "capital_2": {
                "PACKAGE": {1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99, "adicional": 1.08},
                ".COM": {1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99, "adicional": 1.08}
            },
            "capital_3": {
                "PACKAGE": {1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99, "adicional": 1.1988},
                ".COM": {1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99, "adicional": 1.1988}
            },
            "interior_1": {
                "PACKAGE": {1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99, "adicional": 12.3768},
                ".COM": {1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99, "adicional": 15.1848}
            },
            "interior_2": {
                "PACKAGE": {1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99, "adicional": 15.2172},
                ".COM": {1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99, "adicional": 18.6732}
            },
            "interior_3": {
                "PACKAGE": {1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99, "adicional": 18.5652},
                ".COM": {1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99, "adicional": 22.7772}
            }
        }

    def _carregar_lucros(self):
        """LUCRO do revendedor por UF (planilha "final clientes impressão")"""
        return {
            "AC": {1: 14.76, 5: 34.25, 10: 52.95, 20: 103.89, 30: 154.75, 40: 256.02},
            "AL": {1: 12.97, 5: 26.10, 10: 36.22, 20: 66.71, 30: 96.70, 40: 178.31},
            "AP": {1: 19.65, 5: 33.88, 10: 52.58, 20: 103.53, 30: 154.39, 40: 255.66},
            "AM": {1: 20.01, 5: 34.25, 10: 52.95, 20: 103.89, 30: 154.75, 40: 256.02},
            "BA": {1: 12.60, 5: 18.87, 10: 35.85, 20: 66.34, 30: 96.33, 40: 172.89},
            "CE": {1: 14.40, 5: 30.67, 10: 61.11, 20: 122.47, 30: 183.94, 40: 282.51},
            "DF": {1: 11.08, 5: 14.95, 10: 22.17, 20: 48.15, 30: 68.77, 40: 141.62},
            "ES": {1: 11.08, 5: 14.95, 10: 22.17, 20: 48.15, 30: 68.77, 40: 141.62},
            "GO": {1: 11.08, 5: 14.95, 10: 24.70, 20: 48.15, 30: 68.77, 40: 141.62},
            "MA": {1: 12.72, 5: 26.48, 10: 37.43, 20: 69.84, 30: 101.83, 40: 185.57},
            "MT": {1: 12.25, 5: 19.30, 10: 32.08, 20: 69.10, 30: 104.52, 40: 189.05},
            "MS": {1: 13.09, 5: 19.25, 10: 27.83, 20: 49.86, 30: 78.19, 40: 156.89},
            "MG": {1: 12.77, 5: 14.91, 10: 21.38, 20: 38.80, 30: 52.81, 40: 122.57},
            "PA": {1: 12.72, 5: 26.48, 10: 37.43, 20: 69.84, 30: 101.83, 40: 185.57},
            "PB": {1: 13.58, 5: 26.54, 10: 48.48, 20: 94.41, 30: 140.15, 40: 236.71},
            "PR": {1: 11.25, 5: 13.39, 10: 19.85, 20: 37.27, 30: 51.28, 40: 121.05},
            "PE": {1: 14.54, 5: 30.23, 10: 43.62, 20: 81.81, 30: 119.65, 40: 208.57},
            "PI": {1: 13.09, 5: 26.85, 10: 37.80, 20: 70.20, 30: 102.19, 40: 185.94},
            "RJ": {1: 11.25, 5: 13.39, 10: 19.85, 20: 37.27, 30: 51.28, 40: 121.05},
            "RN": {1: 13.58, 5: 26.06, 10: 52.58, 20: 103.53, 30: 154.39, 40: 255.66},
            "RS": {1: 11.70, 5: 15.80, 10: 23.43, 20: 50.89, 30: 72.68, 40: 149.67},
            "RO": {1: 16.92, 5: 39.45, 10: 61.05, 20: 119.91, 30: 178.62, 40: 284.84},
            "RR": {1: 19.65, 5: 33.88, 10: 52.58, 20: 103.53, 30: 154.39, 40: 255.66},
            "SC": {1: 11.25, 5: 13.39, 10: 19.85, 20: 37.27, 30: 51.28, 40: 121.05},
            "SP": {1: 12.66, 5: 14.31, 10: 18.84, 20: 32.88, 30: 37.56, 40: 105.18},
            "SE": {1: 12.60, 5: 25.73, 10: 35.85, 20: 66.34, 30: 96.33, 40: 177.95},
            "TO": {1: 12.72, 5: 26.48, 10: 37.43, 20: 69.84, 30: 101.83, 40: 185.57},
        }

    def _classificar_regiao(self, uf: str, tipo_tarifa: str) -> str:
        if uf in ["SP", "RJ", "MG"] and tipo_tarifa == "CAPITAL":
            return "capital_1"
        elif uf in ["PR", "SC", "RS", "DF", "GO", "MS", "ES", "BA"] and tipo_tarifa == "CAPITAL":
            return "capital_2"
        elif tipo_tarifa == "CAPITAL":
            return "capital_3"
        return "interior_1"

    def _calcular_valor_tabela(self, peso: float, tabela: dict) -> float:
        for p in [1, 5, 10, 20, 30]:
            if peso <= p:
                return tabela[p]
        adicional = tabela.get("adicional", 15.0)
        return round(tabela[30] + (peso - 30) * adicional, 2)

    def calcular(self, cep: str, peso: float, modalidade: str = "PACKAGE", valor_nf: float = 0.0) -> dict:
        info_cep = self.cep_service.buscar(cep)
        if not info_cep:
            return {"erro": f"CEP {cep} não encontrado"}

        uf = info_cep.get("uf", "SP")
        cidade = info_cep.get("cidade", "")
        tipo_tarifa = info_cep.get("tipo_tarifa", "CAPITAL")
        prazo = info_cep.get("prazo", 5)

        regiao = self._classificar_regiao(uf, tipo_tarifa)

        # 1. GLM (custo do revendedor)
        tabela_glm = self.tabelas[regiao][modalidade]
        glm = self._calcular_valor_tabela(peso, tabela_glm)

        # 2. LUCRO (margem do revendedor)
        lucro_uf = self.lucros.get(uf, self.lucros["SP"])
        lucro = None
        for p in sorted(lucro_uf.keys()):
            if peso <= p:
                lucro = lucro_uf[p]
                break
        if lucro is None:
            lucro = lucro_uf[40] * (peso / 40)

        # 3. PREÇO FINAL (valor que o cliente final paga)
        preco_final = glm + lucro

        # 4. AD VALOREM (seguro) - 0,66% se NF > 100
        if valor_nf > 100:
            ad_valorem = round(valor_nf * 0.0066, 2)
        else:
            ad_valorem = 0.0

        # 5. TOTAL
        total = round(preco_final + ad_valorem, 2)

        return {
            "success": True,
            "dados": {
                "cep": cep,
                "uf": uf,
                "cidade": cidade,
                "tipo_tarifa": tipo_tarifa,
                "regiao": regiao,
                "prazo": prazo,
                "peso": peso,
                "modalidade": modalidade,
                "glm": round(glm, 2),
                "lucro": round(lucro, 2),
                "preco_final": round(preco_final, 2),
                "ad_valorem": ad_valorem,
                "total": total,
                "valor_nf": valor_nf
            }
        }