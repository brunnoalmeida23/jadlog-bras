# app/services/frete_calculator.py
from .cep_service import CEPService

class FreteCalculator:
    def __init__(self):
        self.cep_service = CEPService()
        self.glm_base = self._carregar_glm_base()
        self.lucro_capital = self._carregar_lucro_capital()
        self.lucro_interior = self._carregar_lucro_interior()

    # ... (os métodos _carregar_*, _obter_glm, _obter_lucro_capital, _obter_lucro_interior permanecem iguais)

    def calcular(self, cep: str, peso: float, modalidade: str = "PACKAGE", valor_nf: float = 0.0) -> dict:
        info_cep = self.cep_service.buscar(cep)
        if not info_cep:
            return {"erro": f"CEP {cep} não encontrado"}

        uf = info_cep.get("uf", "SP")
        tipo_tarifa = info_cep.get("tipo_tarifa", "CAPITAL")
        regiao_interior = info_cep.get("regiao_interior")  # pode ser None
        cidade = info_cep.get("cidade", "")
        prazo = info_cep.get("prazo", 5)
        seguro_percentual = info_cep.get("seguro_percentual", 0.0066)  # ← NOVO

        # 1. GLM base
        glm = self._obter_glm(peso)

        # 2. LUCRO
        if tipo_tarifa == "CAPITAL":
            lucro = self._obter_lucro_capital(uf, peso)
        else:
            # se regiao_interior for None, usa INT1 como fallback
            regiao = regiao_interior if regiao_interior else "INT1"
            lucro = self._obter_lucro_interior(regiao, peso)

        # 3. PREÇO FINAL
        preco_final = glm + lucro

        # 4. SEGURO (AD VALOREM) - usando percentual da CIDATEN
        ad_valorem = round(valor_nf * seguro_percentual, 2) if valor_nf > 100 else 0.0

        # 5. TOTAL
        total = round(preco_final + ad_valorem, 2)

        return {
            "success": True,
            "dados": {
                "cep": cep,
                "uf": uf,
                "cidade": cidade,
                "tipo_tarifa": tipo_tarifa,
                "regiao_interior": regiao_interior if tipo_tarifa != "CAPITAL" else None,
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