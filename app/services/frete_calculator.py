# app/services/frete_calculator.py
import math

from .tabela_cliente_final import (
    VALORES_ATE_30_CAPITAL,
    VALORES_ATE_30_INTERIOR,
    LUCRO_ACIMA_30,
    GLM_ACIMA_30,
)
from .tabela_dropf import TABELA_DROPF
from .cep_service import CEPService


# WhatsApp oficial da Jadlog Brás
WHATSAPP_CONTATO = "(11) 98964-1426"
WHATSAPP_LINK = "https://api.whatsapp.com/send/?phone=5511989641426"


class FreteCalculator:
    def __init__(self):
        self.valores_capital = VALORES_ATE_30_CAPITAL
        self.valores_interior = VALORES_ATE_30_INTERIOR
        self.lucro_acima_30 = LUCRO_ACIMA_30
        self.glm_acima_30 = GLM_ACIMA_30
        self.tabela_dropf = TABELA_DROPF

    def _arredondar_faixa(self, peso: float) -> int:
        """Arredonda o peso pra próxima faixa de 10 (35->40, 45->50)."""
        faixa = math.ceil(peso / 10) * 10
        if faixa > 100:
            faixa = 100
        return faixa

    def _obter_frete_package_com(self, uf: str, tipo_tarifa: str, peso: float) -> float:
        """Frete base para PACKAGE e .COM (são iguais)."""
        tipo = str(tipo_tarifa or "").strip()

        if peso <= 30:
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
            faixa = self._arredondar_faixa(peso)
            glm_uf = self.glm_acima_30.get(uf, self.glm_acima_30.get("SP", {}))
            glm = glm_uf.get(faixa, 0.0)
            lucro = self.lucro_acima_30.get(faixa, 0.0)
            return glm + lucro

    def _obter_frete_dropf(self, uf: str, peso: float) -> float:
        """Frete base para DROPF (tabela própria, só capital)."""
        dados_uf = self.tabela_dropf.get(uf)
        if not dados_uf:
            return 0.0

        pesos_tabela = sorted(dados_uf.get("pesos", {}).keys())
        if not pesos_tabela:
            return 0.0

        for faixa in pesos_tabela:
            if peso <= faixa:
                return dados_uf["pesos"][faixa]

        return dados_uf["pesos"][pesos_tabela[-1]]

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

        # Bloqueio acima de 100kg
        if peso > 100:
            return {
                "success": True,
                "acima_100kg": True,
                "mensagem": (
                    f"Para cargas acima de 100 kg, entre em contato "
                    f"pelo WhatsApp: {WHATSAPP_CONTATO}"
                ),
                "whatsapp_link": WHATSAPP_LINK,
                "dados": {
                    "cep": cep,
                    "uf": uf,
                    "cidade": cidade,
                    "tipo_tarifa": tipo_tarifa,
                    "prazo": prazo,
                    "peso": peso,
                    "modalidade": modalidade,
                    "valor_nf": valor_nf,
                },
            }

        modalidade_norm = str(modalidade or "").strip().upper()

        if modalidade_norm == "DROPF":
            if tipo_tarifa.startswith("Interior"):
                return {
                    "success": True,
                    "dropf_indisponivel": True,
                    "mensagem": "DROPF disponível apenas para capitais. Use PACKAGE ou .COM.",
                    "dados": {
                        "cep": cep,
                        "uf": uf,
                        "cidade": cidade,
                        "tipo_tarifa": tipo_tarifa,
                        "prazo": prazo,
                        "peso": peso,
                        "modalidade": modalidade,
                        "valor_nf": valor_nf,
                    },
                }
            frete_base = self._obter_frete_dropf(uf, peso)
        else:
            frete_base = self._obter_frete_package_com(uf, tipo_tarifa, peso)

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
