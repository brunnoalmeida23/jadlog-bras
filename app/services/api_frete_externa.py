from __future__ import annotations

import os
import re
from typing import Any

import httpx


URL_API = "https://painel.vocequemanda.com/api.php"
CEP_ORIGEM = os.getenv("CEP_ORIGEM", "12940185")


class ErroApiFrete(Exception):
    pass


def normalizar_cep(cep: str) -> str:
    numeros = re.sub(r"\D", "", str(cep))

    if len(numeros) != 8:
        raise ErroApiFrete("CEP inválido. Digite exatamente 8 números.")

    return numeros


async def consultar_frete(
    cep_destino: str,
    peso: float,
    valor_nf: float,
) -> dict[str, Any]:

    cep_limpo = normalizar_cep(cep_destino)

    if peso <= 0:
        raise ErroApiFrete("O peso deve ser maior que zero.")

    if valor_nf < 0:
        raise ErroApiFrete("O valor da nota não pode ser negativo.")

    payload = {
        "uf": CEP_ORIGEM,
        "cep": cep_limpo,
        "peso": str(peso),
        "valor": str(valor_nf),
    }

    try:
        async with httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
        ) as cliente:
            resposta = await cliente.post(
                URL_API,
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Origin": "https://painel.vocequemanda.com",
                    "Referer": "https://painel.vocequemanda.com/",
                },
            )

        resposta.raise_for_status()
        dados = resposta.json()

    except (httpx.HTTPError, ValueError) as erro:
        raise ErroApiFrete(
            f"Não foi possível consultar o serviço de frete: {erro}"
        ) from erro

    valor_package = dados.get("Package", {}).get("Glm")
    valor_com = dados.get(".Com", {}).get("Glm")

    if valor_package is None or valor_com is None:
        raise ErroApiFrete(
            "A tabela não retornou valores válidos para PACKAGE e .COM."
        )

    return {
        "package": round(float(valor_package), 2),
        "com": round(float(valor_com), 2),
        "retorno_completo": dados,
    }
