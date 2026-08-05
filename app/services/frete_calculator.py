# app/services/frete_calculator.py
"""
CALCULADORA DE FRETE JADLOG BRÁS - VERSÃO COMPLETA
COM TODAS AS TABELAS: CAPITAL 1,2,3 e INTERIOR 1,2,3
COM LUCRO DO CLIENTE
REGRAS:
1. GLM = Tabela base (Capital 1,2,3 ou Interior 1,2,3)
2. LUCRO CLIENTE = Margem do cliente por UF
3. FINAL = GLM + LUCRO CLIENTE
4. Ad Valorem = 0,66% do NF (se NF > R$ 100)
5. TOTAL = FINAL + Ad Valorem
"""

import re
from .cep_service import CEPService


class FreteCalculator:
    """Calculadora de frete completa"""

    def __init__(self):
        self.cep_service = CEPService()
        self.tabelas = self._carregar_tabelas()
        self.lucro_cliente = self._carregar_lucro_cliente()

    def _carregar_tabelas(self):
        """
        Carrega todas as tabelas de preços:
        - Capital 1, 2, 3
        - Interior 1, 2, 3
        - PACKAGE e .COM
        """
        return {
            # ===== CAPITAL 1 =====
            "capital_1": {
                "PACKAGE": {
                    1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99,
                    "adicional": 0.9072
                },
                ".COM": {
                    1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99,
                    "adicional": 0.9072
                }
            },
            # ===== CAPITAL 2 =====
            "capital_2": {
                "PACKAGE": {
                    1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99,
                    "adicional": 1.08
                },
                ".COM": {
                    1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99,
                    "adicional": 1.08
                }
            },
            # ===== CAPITAL 3 =====
            "capital_3": {
                "PACKAGE": {
                    1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99,
                    "adicional": 1.1988
                },
                ".COM": {
                    1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99,
                    "adicional": 1.1988
                }
            },
            # ===== INTERIOR 1 =====
            "interior_1": {
                "PACKAGE": {
                    1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99,
                    "adicional": 12.3768
                },
                ".COM": {
                    1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99,
                    "adicional": 15.1848
                }
            },
            # ===== INTERIOR 2 =====
            "interior_2": {
                "PACKAGE": {
                    1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99,
                    "adicional": 15.2172
                },
                ".COM": {
                    1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99,
                    "adicional": 18.6732
                }
            },
            # ===== INTERIOR 3 =====
            "interior_3": {
                "PACKAGE": {
                    1: 24.99, 5: 49.99, 10: 79.99, 20: 149.99, 30: 229.99,
                    "adicional": 18.5652
                },
                ".COM": {
                    1: 19.99, 5: 39.99, 10: 59.99, 20: 99.99, 30: 159.99,
                    "adicional": 22.7772
                }
            }
        }

    def _carregar_lucro_cliente(self):
        """
        Lucro do cliente por UF e modalidade
        (Extraído da planilha "Preços GLM CLIENTE.xlsx")
        """
        return {
            # ===== SUDESTE =====
            "SP": {
                "PACKAGE": {1: 12.66, 5: 14.31, 10: 18.84, 20: 32.88, 30: 37.56, 40: 105.18},
                ".COM": {1: 11.25, 5: 13.39, 10: 19.85, 20: 37.27, 30: 51.28, 40: 121.05}
            },
            "RJ": {
                "PACKAGE": {1: 11.25, 5: 13.39, 10: 19.85, 20: 37.27, 30: 51.28, 40: 121.05},
                ".COM": {1: 11.25, 5: 13.39, 10: 19.85, 20: 37.27, 30: 51.28, 40: 121.05}
            },
            "MG": {
                "PACKAGE": {1: 12.77, 5: 14.91, 10: 21.38, 20: 38.80, 30: 52.81, 40: 122.57},
                ".COM": {1: 12.77, 5: 14.91, 10: 21.38, 20: 38.80, 30: 52.81, 40: 122.57}
            },
            "ES": {
                "PACKAGE": {1: 11.08, 5: 14.95, 10: 22.17, 20: 48.15, 30: 68.77, 40: 141.62},
                ".COM": {1: 11.08, 5: 14.95, 10: 22.17, 20: 48.15, 30: 68.77, 40: 141.62}
            },
            
            # ===== SUL =====
            "PR": {
                "PACKAGE": {1: 11.25, 5: 13.39, 10: 19.85, 20: 37.27, 30: 51.28, 40: 121.05},
                ".COM": {1: 11.25, 5: 13.39, 10: 19.85, 20: 37.27, 30: 51.28, 40: 121.05}
            },
            "SC": {
                "PACKAGE": {1: 11.25, 5: 13.39, 10: 19.85, 20: 37.27, 30: 51.28, 40: 121.05},
                ".COM": {1: 11.25, 5: 13.39, 10: 19.85, 20: 37.27, 30: 51.28, 40: 121.05}
            },
            "RS": {
                "PACKAGE": {1: 11.70, 5: 15.80, 10: 23.43, 20: 50.89, 30: 72.68, 40: 149.67},
                ".COM": {1: 11.70, 5: 15.80, 10: 23.43, 20: 50.89, 30: 72.68, 40: 149.67}
            },
            
            # ===== CENTRO-OESTE =====
            "DF": {
                "PACKAGE": {1: 11.08, 5: 14.95, 10: 22.17, 20: 48.15, 30: 68.77, 40: 141.62},
                ".COM": {1: 11.08, 5: 14.95, 10: 22.17, 20: 48.15, 30: 68.77, 40: 141.62}
            },
            "GO": {
                "PACKAGE": {1: 11.08, 5: 14.95, 10: 24.70, 20: 48.15, 30: 68.77, 40: 141.62},
                ".COM": {1: 11.08, 5: 14.95, 10: 24.70, 20: 48.15, 30: 68.77, 40: 141.62}
            },
            "MS": {
                "PACKAGE": {1: 13.09, 5: 19.25, 10: 27.83, 20: 49.86, 30: 78.19, 40: 156.89},
                ".COM": {1: 13.09, 5: 19.25, 10: 27.83, 20: 49.86, 30: 78.19, 40: 156.89}
            },
            "MT": {
                "PACKAGE": {1: 12.25, 5: 19.30, 10: 32.08, 20: 69.10, 30: 104.52, 40: 189.05},
                ".COM": {1: 12.25, 5: 19.30, 10: 32.08, 20: 69.10, 30: 104.52, 40: 189.05}
            },
            
            # ===== NORDESTE =====
            "BA": {
                "PACKAGE": {1: 12.60, 5: 18.87, 10: 35.85, 20: 66.34, 30: 96.33, 40: 172.89},
                ".COM": {1: 12.60, 5: 18.87, 10: 35.85, 20: 66.34, 30: 96.33, 40: 172.89}
            },
            "CE": {
                "PACKAGE": {1: 14.40, 5: 30.67, 10: 61.11, 20: 122.47, 30: 183.94, 40: 282.51},
                ".COM": {1: 14.40, 5: 30.67, 10: 61.11, 20: 122.47, 30: 183.94, 40: 282.51}
            },
            "PE": {
                "PACKAGE": {1: 14.54, 5: 30.23, 10: 43.62, 20: 81.81, 30: 119.65, 40: 208.57},
                ".COM": {1: 14.54, 5: 30.23, 10: 43.62, 20: 81.81, 30: 119.65, 40: 208.57}
            },
            "MA": {
                "PACKAGE": {1: 12.72, 5: 26.48, 10: 37.43, 20: 69.84, 30: 101.83, 40: 185.57},
                ".COM": {1: 12.72, 5: 26.48, 10: 37.43, 20: 69.84, 30: 101.83, 40: 185.57}
            },
            "PI": {
                "PACKAGE": {1: 13.09, 5: 26.85, 10: 37.80, 20: 70.20, 30: 102.19, 40: 185.94},
                ".COM": {1: 13.09, 5: 26.85, 10: 37.80, 20: 70.20, 30: 102.19, 40: 185.94}
            },
            "PB": {
                "PACKAGE": {1: 13.58, 5: 26.54, 10: 48.48, 20: 94.41, 30: 140.15, 40: 236.71},
                ".COM": {1: 13.58, 5: 26.54, 10: 48.48, 20: 94.41, 30: 140.15, 40: 236.71}
            },
            "RN": {
                "PACKAGE": {1: 13.58, 5: 26.06, 10: 52.58, 20: 103.53, 30: 154.39, 40: 255.66},
                ".COM": {1: 13.58, 5: 26.06, 10: 52.58, 20: 103.53, 30: 154.39, 40: 255.66}
            },
            "SE": {
                "PACKAGE": {1: 12.60, 5: 25.73, 10: 35.85, 20: 66.34, 30: 96.33, 40: 177.95},
                ".COM": {1: 12.60, 5: 25.73, 10: 35.85, 20: 66.34, 30: 96.33, 40: 177.95}
            },
            "AL": {
                "PACKAGE": {1: 12.97, 5: 26.10, 10: 36.22, 20: 66.71, 30: 96.70, 40: 178.31},
                ".COM": {1: 12.97, 5: 26.10, 10: 36.22, 20: 66.71, 30: 96.70, 40: 178.31}
            },
            
            # ===== NORTE =====
            "AC": {
                "PACKAGE": {1: 14.76, 5: 34.25, 10: 52.95, 20: 103.89, 30: 154.75, 40: 256.02},
                ".COM": {1: 14.76, 5: 34.25, 10: 52.95, 20: 103.89, 30: 154.75, 40: 256.02}
            },
            "AM": {
                "PACKAGE": {1: 20.01, 5: 34.25, 10: 52.95, 20: 103.89, 30: 154.75, 40: 256.02},
                ".COM": {1: 20.01, 5: 34.25, 10: 52.95, 20: 103.89, 30: 154.75, 40: 256.02}
            },
            "AP": {
                "PACKAGE": {1: 19.65, 5: 33.88, 10: 52.58, 20: 103.53, 30: 154.39, 40: 255.66},
                ".COM": {1: 19.65, 5: 33.88, 10: 52.58, 20: 103.53, 30: 154.39, 40: 255.66}
            },
            "PA": {
                "PACKAGE": {1: 12.72, 5: 26.48, 10: 37.43, 20: 69.84, 30: 101.83, 40: 185.57},
                ".COM": {1: 12.72, 5: 26.48, 10: 37.43, 20: 69.84, 30: 101.83, 40: 185.57}
            },
            "RO": {
                "PACKAGE": {1: 16.92, 5: 39.45, 10: 61.05, 20: 119.91, 30: 178.62, 40: 284.84},
                ".COM": {1: 16.92, 5: 39.45, 10: 61.05, 20: 119.91, 30: 178.62, 40: 284.84}
            },
            "RR": {
                "PACKAGE": {1: 19.65, 5: 33.88, 10: 52.58, 20: 103.53, 30: 154.39, 40: 255.66},
                ".COM": {1: 19.65, 5: 33.88, 10: 52.58, 20: 103.53, 30: 154.39, 40: 255.66}
            },
            "TO": {
                "PACKAGE": {1: 12.72, 5: 26.48, 10: 37.43, 20: 69.84, 30: 101.83, 40: 185.57},
                ".COM": {1: 12.72, 5: 26.48, 10: 37.43, 20: 69.84, 30: 101.83, 40: 185.57}
            }
        }

    def _classificar_regiao(self, uf: str, tipo_tarifa: str) -> str:
        """Classifica a região baseado na UF e tipo de tarifa"""
        # Capital 1: SP, RJ, MG
        if uf in ["SP", "RJ", "MG"] and tipo_tarifa == "CAPITAL":
            return "capital_1"
        # Capital 2: PR, SC, RS, DF, GO, MS, ES, BA
        elif uf in ["PR", "SC", "RS", "DF", "GO", "MS", "ES", "BA"] and tipo_tarifa == "CAPITAL":
            return "capital_2"
        # Capital 3: AM, AC, AP, PA, RO, RR, TO, MT, MA, PI, PB, RN, SE, AL, CE, PE
        elif tipo_tarifa == "CAPITAL":
            return "capital_3"
        # Interior 1, 2, 3 (definido pela Cidaten)
        elif tipo_tarifa == "INTERIOR":
            return "interior_1"  # Default
        return "capital_1"

    def _calcular_valor_tabela(self, peso: float, tabela: dict) -> float:
        """Calcula o valor baseado na tabela de faixas de peso"""
        # Pesos fixos
        pesos_fixos = [1, 5, 10, 20, 30]
        for p in pesos_fixos:
            if peso <= p:
                return tabela[p]

        # Peso > 30kg - usar KG ADICIONAL
        adicional = tabela.get("adicional", 15.0)
        peso_excedente = peso - 30
        valor_base = tabela[30]
        valor_total = valor_base + (peso_excedente * adicional)

        return round(valor_total, 2)

    def calcular(self, cep: str, peso: float, modalidade: str = "PACKAGE", 
                 valor_nf: float = 0.0) -> dict:
        """
        Calcula o frete completo com:
        - GLM (base) - Capital 1,2,3 ou Interior 1,2,3
        - LUCRO DO CLIENTE (por UF)
        - FINAL = GLM + LUCRO
        - Ad Valorem (seguro)
        - TOTAL = FINAL + Ad Valorem

        Args:
            cep: CEP de destino
            peso: Peso em kg
            modalidade: 'PACKAGE' ou '.COM'
            valor_nf: Valor da nota fiscal

        Returns:
            dict: Resultado completo
        """
        # 1. Buscar informações do CEP
        info_cep = self.cep_service.buscar(cep)
        if not info_cep:
            return {"erro": f"CEP {cep} não encontrado"}

        uf = info_cep.get("uf", "SP")
        cidade = info_cep.get("cidade", "")
        tipo_tarifa = info_cep.get("tipo_tarifa", "CAPITAL")
        prazo = info_cep.get("prazo", 5)

        # 2. Classificar a região
        regiao = self._classificar_regiao(uf, tipo_tarifa)

        # 3. Calcular GLM (base)
        tabela_glm = self.tabelas[regiao][modalidade]
        glm = self._calcular_valor_tabela(peso, tabela_glm)

        # 4. Calcular LUCRO DO CLIENTE
        lucro_uf = self.lucro_cliente.get(uf, self.lucro_cliente["SP"])
        tabela_lucro = lucro_uf.get(modalidade, lucro_uf["PACKAGE"])
        
        # Encontrar a faixa de peso para o lucro
        pesos_lucro = sorted([p for p in tabela_lucro.keys() if isinstance(p, int)])
        lucro = None
        for p in pesos_lucro:
            if peso <= p:
                lucro = tabela_lucro[p]
                break
        
        if lucro is None:
            # Peso > maior faixa (40kg+)
            lucro = tabela_lucro[40] * (peso / 40)

        # 5. FINAL (GLM + Lucro do cliente)
        final = glm + lucro

        # 6. Ad Valorem (seguro) - APENAS SE NF > 100
        if valor_nf > 100:
            ad_valorem = round(valor_nf * 0.0066, 2)
        else:
            ad_valorem = 0.0

        # 7. TOTAL
        total = round(final + ad_valorem, 2)

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
                "lucro_cliente": round(lucro, 2),
                "final": round(final, 2),
                "ad_valorem": ad_valorem,
                "total": total,
                "valor_nf": valor_nf
            }
        }