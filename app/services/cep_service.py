import json
import os
import re
from typing import Optional


class CEPService:
    """Consulta informações tarifárias e operacionais por prefixo de CEP."""

    def __init__(self) -> None:
        self.arquivo_base = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "base_ceps.json",
        )

        self.dados_cep = self._carregar_dados()

    def _carregar_dados(self) -> dict:
        if not os.path.exists(self.arquivo_base):
            raise FileNotFoundError(
                f"Base de CEPs não encontrada: {self.arquivo_base}"
            )

        try:
            with open(
                self.arquivo_base,
                "r",
                encoding="utf-8",
            ) as arquivo:
                dados = json.load(arquivo)

        except (json.JSONDecodeError, OSError) as erro:
            raise RuntimeError(
                f"Erro ao carregar a base de CEPs: {erro}"
            ) from erro

        if not isinstance(dados, dict):
            raise RuntimeError(
                "A base de CEPs possui formato inválido."
            )

        return dados

    @staticmethod
    def normalizar_cep(cep: str) -> str:
        cep_limpo = re.sub(r"\D", "", str(cep))

        if len(cep_limpo) != 8:
            raise ValueError(
                "CEP inválido. Digite exatamente 8 números."
            )

        return cep_limpo

    def buscar(self, cep: str) -> Optional[dict]:
        cep_limpo = self.normalizar_cep(cep)

        prefixo = cep_limpo[:5]
        resultado = self.dados_cep.get(prefixo)

        if not resultado:
            return None

        return {
            "cidade": str(resultado.get("cidade", "")).strip(),
            "uf": str(resultado.get("uf", "")).strip().upper(),
            "tipo_tarifa": str(
                resultado.get("tipo_tarifa", "")
            ).strip(),
            "prazo": int(resultado.get("prazo", 0) or 0),
        }