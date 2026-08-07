from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

# Local development: load the root .env. On Vercel, environment variables
# configured in Project Settings take precedence because override=False.
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ENV_PATH, override=False)


class SupabaseConfigError(RuntimeError):
    pass


class SupabaseService:
    """Small Supabase REST client for the tables used by this application.

    Using the REST API keeps the dependency tree small and is enough for the
    CRUD operations required by the simulator.
    """

    def __init__(self) -> None:
        self.url = (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
        self.key = (os.getenv("SUPABASE_KEY") or "").strip()
        if not self.url or not self.key:
            raise SupabaseConfigError(
                "SUPABASE_URL e SUPABASE_KEY não estão configurados."
            )
        self.base_url = f"{self.url}/rest/v1"
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def somente_numeros(valor: str) -> str:
        return re.sub(r"\D", "", str(valor or ""))

    def _request(self, method: str, table: str, **kwargs: Any) -> requests.Response:
        headers = dict(self.headers)
        headers.update(kwargs.pop("headers", {}) or {})
        response = requests.request(
            method,
            f"{self.base_url}/{table}",
            headers=headers,
            timeout=12,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def buscar_cliente_por_cpf(self, cpf: str) -> dict[str, Any] | None:
        cpf_limpo = self.somente_numeros(cpf)
        response = self._request(
            "GET",
            "clientes",
            params={"select": "*", "cpf_cnpj": f"eq.{cpf_limpo}", "limit": "1"},
        )
        dados = response.json()
        return dados[0] if dados else None

    def cadastrar_cliente(self, dados: dict[str, Any]) -> dict[str, Any] | None:
        payload = dict(dados)
        if "cpf_cnpj" in payload:
            payload["cpf_cnpj"] = self.somente_numeros(payload["cpf_cnpj"])
        response = self._request(
            "POST",
            "clientes",
            json=payload,
            headers={"Prefer": "return=representation"},
        )
        resultado = response.json()
        return resultado[0] if resultado else None

    def salvar_cotacao(self, dados: dict[str, Any]) -> dict[str, Any] | None:
        response = self._request(
            "POST",
            "cotacoes",
            json=dados,
            headers={"Prefer": "return=representation"},
        )
        resultado = response.json()
        return resultado[0] if resultado else None

    def buscar_cotacao_por_numero(self, numero: str) -> dict[str, Any] | None:
        response = self._request(
            "GET",
            "cotacoes",
            params={"select": "*", "numero": f"eq.{numero.strip()}", "limit": "1"},
        )
        dados = response.json()
        return dados[0] if dados else None

    def listar_cotacoes_por_cpf(self, cpf: str, limite: int = 50) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "cotacoes",
            params={
                "select": "*",
                "cpf_cliente": f"eq.{self.somente_numeros(cpf)}",
                "order": "data_criacao.desc",
                "limit": str(max(1, min(limite, 100))),
            },
        )
        return response.json() or []


# Do NOT instantiate at import time. Missing Vercel variables must not crash
# the entire application before a route can return a useful error.
def get_supabase_service() -> SupabaseService:
    return SupabaseService()
