from __future__ import annotations

import json
import os

from fastapi import APIRouter, Form, Query
from fastapi.responses import JSONResponse

from app.services.cliente_service import ClienteService


router = APIRouter(prefix="/api", tags=["API"])


@router.post("/buscar-cliente")
async def buscar_cliente(
    termo: str = Form(...),
):
    service = ClienteService()
    return service.buscar(termo)


@router.post("/salvar-cliente")
async def salvar_cliente(
    cpf_cnpj: str = Form(...),
    nome: str = Form(""),
    razao_social: str = Form(""),
    endereco: str = Form(""),
    cidade: str = Form(""),
    uf: str = Form(""),
    cep: str = Form(""),
    telefone: str = Form(""),
):
    service = ClienteService()

    resultado = service.salvar_cliente(
        cpf_cnpj=cpf_cnpj,
        nome=nome,
        razao_social=razao_social,
        endereco=endereco,
        cidade=cidade,
        uf=uf,
        cep=cep,
        telefone=telefone,
    )

    if not resultado["success"]:
        return JSONResponse(
            status_code=400,
            content=resultado,
        )

    return resultado


@router.get("/consultar-cotacao")
async def consultar_cotacao(
    numero_cotacao: str = Query(...),
):
    arquivo_cotacoes = "cotacoes.json"

    if not os.path.exists(arquivo_cotacoes):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "Nenhuma cotação encontrada.",
            },
        )

    try:
        with open(
            arquivo_cotacoes,
            "r",
            encoding="utf-8",
        ) as arquivo:
            cotacoes = json.load(arquivo)

    except (OSError, json.JSONDecodeError):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Erro ao ler as cotações.",
            },
        )

    numero_procurado = numero_cotacao.strip().upper()

    for cotacao in cotacoes:
        numero = str(
            cotacao.get("numero_cotacao", "")
        ).strip().upper()

        if numero == numero_procurado:
            return {
                "success": True,
                "dados": cotacao,
            }

    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": (
                f"Cotação {numero_cotacao} não encontrada."
            ),
        },
    )