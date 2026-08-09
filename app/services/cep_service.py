# app/services/cep_service.py
from __future__ import annotations

import bisect
import re
from typing import Optional

import pandas as pd


class CEPService:
    """Consulta a CIDATEN por intervalo de CEP."""

    def __init__(self, arquivo_cidaten: str = "Cidaten_2026.xlsx"):
        self.arquivo = arquivo_cidaten
        # inicio, fim, uf, localidade, tipo, prazo, frap_fob, seguro
        self.dados = []
        self.inicios = []
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

            inicio, fim = self._parse_intervalo(row["Cep"])
            uf = str(row["UF"]).strip().upper()
            cidade = str(row["Localidade"]).strip()
            tipo = " ".join(str(row["Tipo Tarifa"]).strip().split())
            prazo = int(row["Prazo Rodo"]) if pd.notna(row["Prazo Rodo"]) else 0
            frap = str(row["Frap (Fob)"]).strip() if pd.notna(row["Frap (Fob)"]) else ""
            seguro = float(row["% Seguro"]) if pd.notna(row["% Seguro"]) else 0.0

            registros.append((inicio, fim, uf, cidade, tipo, prazo, frap, seguro))

        registros.sort(key=lambda x: x[0])
        self.dados = registros
        self.inicios = [r[0] for r in registros]

    def buscar(self, cep):
        cep_int = self._normalizar_cep(cep)
        if cep_int is None:
            return None

        pos = bisect.bisect_right(self.inicios, cep_int) - 1
        if pos < 0:
            return None

        inicio, fim, uf, cidade, tipo, prazo, frap, seguro = self.dados[pos]
        if not (inicio <= cep_int <= fim):
            return None

        return {
            "cep": f"{cep_int:08d}",
            "cep_inicio": f"{inicio:08d}",
            "cep_fim": f"{fim:08d}",
            "uf": uf,
            "cidade": cidade,
            "tipo_tarifa": tipo,
            "prazo": prazo,
            "frap_fob": frap,
            "seguro_percentual": seguro,
        }
