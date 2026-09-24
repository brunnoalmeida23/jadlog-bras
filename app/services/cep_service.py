# app/services/cep_service.py
from __future__ import annotations

import re
from typing import Optional

import pandas as pd


class CEPService:
    """Consulta a CIDATEN por intervalo de CEP."""

    def __init__(self, arquivo_cidaten: str = "Cidaten_2026.xlsx"):
        self.arquivo = arquivo_cidaten
        self.dados: list[dict] = []
        self._carregar()

    @staticmethod
    def _normalizar_cep(cep) -> Optional[int]:
        texto = re.sub(r"\D", "", str(cep or ""))
        if len(texto) != 8:
            return None
        return int(texto)

    @staticmethod
    def _parse_intervalo(valor) -> tuple[int, int]:
        texto = str(valor).strip()
        numeros = re.findall(r"\d+", texto)
        if not numeros:
            raise ValueError(f"Intervalo de CEP inválido: {valor!r}")
        if len(numeros) == 1:
            inicio = fim = int(numeros[0])
        else:
            inicio, fim = int(numeros[0]), int(numeros[1])
        return inicio, fim

    @staticmethod
    def _parse_seguro(valor) -> float:
        """Aceita 0.0066 (decimal), 0,66% (texto), 1% (texto), 0.01 (decimal)."""
        if pd.isna(valor):
            return 0.0

        if isinstance(valor, (int, float)):
            return float(valor)

        texto = str(valor).strip()

        if "%" in texto:
            texto = texto.replace("%", "").strip()
            texto = texto.replace(",", ".")
            try:
                return float(texto) / 100.0
            except ValueError:
                return 0.0

        texto = texto.replace(",", ".")
        try:
            return float(texto)
        except ValueError:
            return 0.0

    def _carregar(self):
        try:
            df = pd.read_excel(self.arquivo, sheet_name="Cidaten", header=1)
        except Exception as exc:
            raise RuntimeError(f"Erro ao carregar CIDATEN: {exc}") from exc

        obrigatorias = {
            "UF", "Localidade", "Cep", "Prazo Rodo",
            "Tipo Tarifa", "Frap (Fob)", "% Seguro",
        }
        faltantes = obrigatorias.difference(df.columns)
        if faltantes:
            raise RuntimeError(f"CIDATEN sem colunas obrigatórias: {sorted(faltantes)}")

        registros = []
        for _, row in df.iterrows():
            if pd.isna(row["Cep"]):
                continue

            try:
                inicio, fim = self._parse_intervalo(row["Cep"])
            except ValueError:
                continue

            uf = str(row["UF"]).strip().upper()
            cidade = str(row["Localidade"]).strip()
            tipo = " ".join(str(row["Tipo Tarifa"]).strip().split())
            prazo = int(row["Prazo Rodo"]) if pd.notna(row["Prazo Rodo"]) else 0
            frap = str(row["Frap (Fob)"]).strip() if pd.notna(row["Frap (Fob)"]) else ""
            seguro = self._parse_seguro(row["% Seguro"])

            registros.append({
                "inicio": inicio,
                "fim": fim,
                "uf": uf,
                "cidade": cidade,
                "tipo": tipo,
                "prazo": prazo,
                "frap": frap,
                "seguro": seguro,
                "amplitude": fim - inicio,
            })

        registros.sort(key=lambda r: r["amplitude"])
        self.dados = registros

    @staticmethod
    def _forcar_capital_sp(cep_int: int, resultado: dict) -> dict:
        """Regra especial: CEPs de São Paulo que estão caindo como Interior
        mas deveriam ser Capital.

        A Cidaten está incompleta para a Zona Leste de SP.
        Faixa problemática: 08000000 a 08499999 (Itaquera, Guaianases, etc.)
        """
        if resultado.get("uf") != "SP":
            return resultado

        if resultado.get("tipo_tarifa", "").startswith("Interior"):
            # Zona Leste de SP (08000-000 a 08499-999)
            if 8000000 <= cep_int <= 8499999:
                resultado["tipo_tarifa"] = "Capital"
                resultado["_forcado_capital"] = True
                # Corrige o % Seguro para Capital (0,66%)
                if resultado.get("seguro_percentual", 0) > 0.0066:
                    resultado["seguro_percentual"] = 0.0066

        return resultado

    def buscar(self, cep):
        cep_int = self._normalizar_cep(cep)
        if cep_int is None:
            return None

        candidatos = [
            r for r in self.dados
            if r["inicio"] <= cep_int <= r["fim"]
        ]

        if not candidatos:
            return None

        r = candidatos[0]

        resultado = {
            "cep": f"{cep_int:08d}",
            "cep_inicio": f"{r['inicio']:08d}",
            "cep_fim": f"{r['fim']:08d}",
            "uf": r["uf"],
            "cidade": r["cidade"],
            "tipo_tarifa": r["tipo"],
            "prazo": r["prazo"],
            "frap_fob": r["frap"],
            "seguro_percentual": r["seguro"],
        }

        # Aplica regra especial: força Capital para CEPs de SP que estão como Interior
        resultado = self._forcar_capital_sp(cep_int, resultado)

        return resultado