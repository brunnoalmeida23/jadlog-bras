# app/services/frete_calculator.py
from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP

from .cep_service import CEPService
from .tarifas_capital_v32 import (
    GLM_CAPITAL_PONTOS,
    LUCRO_FAIXAS,
    PRECO_PROMOCIONAL_CAPITAL,
)
from .tarifas_glm_v32 import PESOS_TABELA, TABELAS_GLM


CENTAVOS = Decimal("0.01")
VERSAO_MOTOR = "3.2"


def _d(valor) -> Decimal:
    return Decimal(str(valor))


def _moeda(valor) -> float:
    return float(_d(valor).quantize(CENTAVOS, rounding=ROUND_HALF_UP))


class FreteCalculator:
    """
    Motor V3.2 - Jadlog Brás.

    Entradas:
      CEP de destino, peso, valor da NF e modalidade.

    Fluxo:
      CEP -> CIDATEN -> classificação/UF/prazo/% seguro
      -> tabela aplicável -> GLM do peso
      -> lucro da faixa -> ad valorem -> total.

    Observação:
      Os detalhes de composição retornados servem para auditoria do backend.
      A interface do cliente final não deve exibi-los.
    """

    TIPOS_GLM = {
        "Capital 1", "Capital 2", "Capital 3",
        "Interior 1", "Interior 2", "Interior 3",
    }
    FAIXAS_LUCRO = (1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)

    def __init__(self):
        self.cep_service = CEPService()

    @staticmethod
    def _normalizar_modalidade(modalidade: str) -> str:
        mod = (modalidade or "").strip().upper()
        if mod in {"PACKAGE", "PACK", ".PACKAGE"}:
            return "PACKAGE"
        if mod in {".COM", "COM"}:
            return ".COM"
        raise ValueError("Modalidade inválida.")

    @staticmethod
    def _normalizar_tipo(tipo: str) -> str:
        return " ".join((tipo or "").strip().split())

    @classmethod
    def _faixa_lucro(cls, peso: float) -> int:
        for faixa in cls.FAIXAS_LUCRO:
            if peso <= faixa:
                return faixa
        raise ValueError("Peso acima de 100 kg: cotação automática não homologada.")

    @classmethod
    def _lucro(cls, peso: float) -> tuple[int, Decimal]:
        faixa = cls._faixa_lucro(peso)
        return faixa, _d(LUCRO_FAIXAS[faixa])

    @staticmethod
    def _faixa_promocional(peso: float) -> int:
        for faixa in (1, 5, 10, 20, 30):
            if peso <= faixa:
                return faixa
        raise ValueError("Peso fora da faixa promocional.")

    @staticmethod
    def _peso_glm_ate_30(peso: float) -> float:
        """
        Usa a menor coluna GLM que comporte o peso:
        0,25 / 0,50 / 0,75 / 1 / 2 / ... / 30.
        """
        if peso <= 0:
            raise ValueError("Peso deve ser maior que zero.")
        for faixa in PESOS_TABELA:
            if peso <= faixa + 1e-12:
                return float(faixa)
        return 30.0

    @staticmethod
    def _kg_adicionais(peso: float) -> int:
        """
        Acima de 30 kg cobra o KG ADICIONAL da tabela.
        Fração de quilo é arredondada para o próximo kg tarifável.
        """
        if peso <= 30:
            return 0
        return int(math.ceil(peso - 30.0 - 1e-12))

    def _glm_regional(self, uf: str, tipo: str, modalidade: str, peso: float):
        try:
            tabela = TABELAS_GLM[modalidade][tipo][uf]
        except KeyError as exc:
            raise ValueError(
                f"Não existe GLM para {uf} / {tipo} / {modalidade}."
            ) from exc

        if peso <= 30:
            peso_tabela = self._peso_glm_ate_30(peso)
            glm = _d(tabela["pesos"][peso_tabela])
            adicionais = 0
        else:
            peso_tabela = 30.0
            adicionais = self._kg_adicionais(peso)
            glm = _d(tabela["pesos"][30.0]) + _d(tabela["adicional"]) * adicionais

        return glm, peso_tabela, adicionais, _d(tabela["adicional"])

    def _glm_capital_acima_30(self, uf: str, peso: float):
        """Calcula a classificação literal ``Capital`` acima de 30 kg.

        Fonte: aba ``SP CAPITAL`` da PLANILHA-CAP-INT.xlsx.

        Essa aba NÃO possui KG ADICIONAL e NÃO separa PACKAGE de .COM. Ela
        fornece pontos comerciais homologados em 40, 50, ..., 100 kg.
        Portanto, qualquer peso entre duas faixas usa a próxima faixa que o
        comporta, sem interpolação matemática e sem inventar um adicional.

        Exemplos:
          31..40 kg -> coluna 40 kg
          41..50 kg -> coluna 50 kg
          71..80 kg -> coluna 80 kg
        """
        pontos = GLM_CAPITAL_PONTOS.get(uf)
        if not pontos:
            raise ValueError(f"Sem tabela de Capital para UF {uf}.")

        peso_tarifavel = int(math.ceil(peso - 1e-12))
        for faixa in (40, 50, 60, 70, 80, 90, 100):
            if peso_tarifavel <= faixa:
                return _d(pontos[faixa]), float(faixa), 0, Decimal("0")

        raise ValueError("Peso acima de 100 kg: cotação automática não homologada.")

    def calcular(
        self,
        cep: str,
        peso: float,
        modalidade: str = "PACKAGE",
        valor_nf: float = 0.0,
    ) -> dict:
        try:
            peso = float(peso)
            valor_nf = float(valor_nf)
            modalidade = self._normalizar_modalidade(modalidade)

            if peso <= 0:
                raise ValueError("Peso deve ser maior que zero.")
            if peso > 100:
                raise ValueError("Peso acima de 100 kg: consulte um atendente.")
            if valor_nf < 0:
                raise ValueError("Valor da nota fiscal não pode ser negativo.")

            info = self.cep_service.buscar(cep)
            if not info:
                raise ValueError("CEP não encontrado na CIDATEN.")

            uf = str(info["uf"]).strip().upper()
            cidade = str(info["cidade"]).strip()
            tipo = self._normalizar_tipo(info["tipo_tarifa"])
            prazo = int(info.get("prazo", 0) or 0)
            seguro_percentual = _d(info.get("seguro_percentual", 0) or 0)

            peso_tabela = None
            kg_adicionais = 0
            adicional_unitario = Decimal("0")
            faixa_lucro = None
            lucro = Decimal("0")

            if tipo == "Capital":
                tabela_aplicada = "SP CAPITAL / DESTINOS CAPITAL"

                if peso <= 30:
                    faixa_promo = self._faixa_promocional(peso)
                    glm = _d(PRECO_PROMOCIONAL_CAPITAL[faixa_promo])
                    preco_sem_seguro = glm
                    peso_tabela = float(faixa_promo)
                    regra = "CAPITAL_PROMOCIONAL"
                else:
                    glm, peso_tabela, kg_adicionais, adicional_unitario = (
                        self._glm_capital_acima_30(uf, peso)
                    )
                    faixa_lucro, lucro = self._lucro(peso)
                    preco_sem_seguro = glm + lucro
                    regra = "CAPITAL_FAIXA_CAP_X_INT_MAIS_LUCRO"

            elif tipo in self.TIPOS_GLM:
                tabela_aplicada = tipo
                glm, peso_tabela, kg_adicionais, adicional_unitario = self._glm_regional(
                    uf, tipo, modalidade, peso
                )
                faixa_lucro, lucro = self._lucro(peso)
                preco_sem_seguro = glm + lucro
                regra = "GLM_MODALIDADE_MAIS_LUCRO"

            else:
                raise ValueError(f"Classificação CIDATEN não homologada: {tipo}")

            seguro_aplicado = bool(valor_nf > 100 and seguro_percentual > 0)
            seguro = (
                _d(valor_nf) * seguro_percentual
                if seguro_aplicado
                else Decimal("0")
            )

            preco_final = _moeda(preco_sem_seguro)
            seguro_final = _moeda(seguro)
            total = _moeda(_d(preco_final) + _d(seguro_final))

            return {
                "success": True,
                "dados": {
                    # Campos necessários à interface/recibo
                    "cep": info["cep"],
                    "uf": uf,
                    "cidade": cidade,
                    "tipo_tarifa": tipo,
                    "prazo": prazo,
                    "peso": peso,
                    "modalidade": modalidade,
                    "preco_final": preco_final,
                    "frete": preco_final,
                    "seguro": seguro_final,
                    "ad_valorem": seguro_final,
                    "total": total,

                    # Auditoria interna - não exibir ao cliente final
                    "_auditoria": {
                        "classificacao_cidaten": tipo,
                        "cep_faixa_inicio": info.get("cep_inicio"),
                        "cep_faixa_fim": info.get("cep_fim"),
                        "frap_fob": info.get("frap_fob", ""),
                        "tabela_aplicada": tabela_aplicada,
                        "modalidade_aplicada": modalidade,
                        "peso_tabela_glm": peso_tabela,
                        "kg_adicionais": kg_adicionais,
                        "kg_adicional_unitario": _moeda(adicional_unitario),
                        "glm": _moeda(glm),
                        "faixa_lucro": faixa_lucro,
                        "lucro": _moeda(lucro),
                        "seguro_percentual": float(seguro_percentual),
                        "seguro_aplicado": seguro_aplicado,
                        "regra_calculo": regra,
                        "versao_motor": VERSAO_MOTOR,
                        "fonte_cep": "CIDATEN",
                        "fonte_tarifa": "CAP X INT + GLM LIEV",
                    },
                },
            }

        except ValueError as exc:
            return {"success": False, "erro": str(exc)}
        except Exception as exc:
            return {"success": False, "erro": f"Falha no cálculo do frete: {exc}"}
