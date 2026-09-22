# app/services/frete_calculator.py
import math

from .tabela_cliente_final import (
    VALORES_ATE_30_CAPITAL,
    VALORES_ATE_30_INTERIOR,
    LUCRO_ACIMA_30,
    GLM_ACIMA_30,
)
from .cep_service import CEPService


class FreteCalculator:
    def __init__(self):
        self.valores_capital = VALORES_ATE_30_CAPITAL
        self.valores_interior = VALORES_ATE_30_INTERIOR
        self.lucro_acima_30 = LUCRO_ACIMA_30
        self.glm_acima_30 = GLM_ACIMA_30

    def _arredondar_faixa(self, peso: float) -> int:
        """Arredonda o peso pra próxima faixa de 10 (35->40, 45->50)."""
        faixa = math.ceil(peso / 10) * 10
        if faixa > 100:
            faixa = 100
        return faixa

    def _obter_frete_base(self, uf: str, tipo_tarifa: str, peso: float) -> float:
        tipo = str(tipo_tarifa or "").strip()

        if peso <= 30:
            # Arredonda pra próxima faixa até 30
            if peso <= 1:
                peso_faixa = 1
            elif peso <= 5:
                peso_faixa = 5
            elif peso <= 10:
                peso_faixa = 10
            elif peso <= 20:
                peso_faixa = 20
            else:
                peso_faixa = 30

            if tipo.startswith("Interior"):
                return self.valores_interior.get(peso_faixa, 0.0)
            else:
                return self.valores_capital.get(peso_faixa, 0.0)
        else:
            # Acima de 30kg: GLM[UF] + LUCRO[faixa]
            faixa = self._arredondar_faixa(peso)
            glm_uf = self.glm_acima_30.get(uf, self.glm_acima_30.get("SP", {}))
            glm = glm_uf.get(faixa, 0.0)
            lucro = self.lucro_acima_30.get(faixa, 0.0)
            return glm + lucro

    def calcular(self, cep: str, peso: float, modalidade: str = "PACKAGE", valor_nf: float = 0.0) -> dict:
        """Calcula o frete baseado no CEP, peso, modalidade e valor da NF."""
        cep_service = CEPService()
        info_cep = cep_service.buscar(cep)

        if not info_cep:
            return {"erro": f"CEP {cep} não encontrado"}

        uf = info_cep.get("uf", "SP")
        tipo_tarifa = info_cep.get("tipo_tarifa", "Capital")
        cidade = info_cep.get("cidade", "")
        prazo = info_cep.get("prazo", 5)
        seguro_percentual = 0.0066

        # Frete base (PACKAGE e .COM são IGUAIS)
        frete_base = self._obter_frete_base(uf, tipo_tarifa, peso)

        # Ad valorem (só se NF > R$ 100)
        ad_valorem = 0.0
        if valor_nf > 100.0:
            ad_valorem = round(valor_nf * seguro_percentual, 2)

        total = round(frete_base + ad_valorem, 2)

        return {
            "success": True,
            "dados": {
                "cep": cep,
                "uf": uf,
                "cidade": cidade,
                "tipo_tarifa": tipo_tarifa,
                "prazo": prazo,
                "peso": peso,
                "modalidade": modalidade,
                "frete_base": round(frete_base, 2),
                "ad_valorem": round(ad_valorem, 2),
                "total": total,
                "valor_nf": valor_nf,
            },
        }
