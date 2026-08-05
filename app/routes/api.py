# app/routes/api.py
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import os
import json
import re

from app.services.cliente_service import ClienteService
from app.services.frete_calculator import FreteCalculator
from app.utils.helpers import gerar_cotacao_id

router = APIRouter(prefix="/api", tags=["API"])


@router.post("/buscar-cliente")
async def buscar_cliente(cpf_cnpj: str = Form(...)):
    """Busca cliente por CPF/CNPJ"""
    service = ClienteService()
    resultado = service.buscar_por_documento(cpf_cnpj)
    return resultado


@router.post("/salvar-cliente")
async def salvar_cliente(
    cpf_cnpj: str = Form(...),
    nome: str = Form(...),
    razao_social: str = Form(""),
    endereco: str = Form(""),
    cidade: str = Form(""),
    uf: str = Form(""),
    cep: str = Form(""),
    telefone: str = Form("")
):
    """Salva um novo cliente"""
    service = ClienteService()
    resultado = service.salvar_cliente(
        cpf_cnpj=cpf_cnpj,
        nome=nome,
        razao_social=razao_social,
        endereco=endereco,
        cidade=cidade,
        uf=uf,
        cep=cep,
        telefone=telefone
    )
    return resultado


@router.get("/consultar-cotacao")
async def consultar_cotacao(numero_cotacao: str):
    """Consulta uma cotação pelo número"""
    cotacoes_file = "cotacoes.json"

    if not os.path.exists(cotacoes_file):
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Nenhuma cotação encontrada"}
        )

    try:
        with open(cotacoes_file, "r") as f:
            cotacoes = json.load(f)
    except:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Erro ao ler arquivo de cotações"}
        )

    for cotacao in cotacoes:
        if cotacao.get("numero_cotacao") == numero_cotacao:
            return {"success": True, "dados": cotacao}

    return JSONResponse(
        status_code=404,
        content={"success": False, "message": f"Cotação {numero_cotacao} não encontrada"}
    )


@router.get("/imprimir-recibo")
async def imprimir_recibo(numero_cotacao: str):
    """Gera e retorna o recibo em PDF (simulado)"""
    cotacoes_file = "cotacoes.json"

    if not os.path.exists(cotacoes_file):
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Nenhuma cotação encontrada"}
        )

    try:
        with open(cotacoes_file, "r") as f:
            cotacoes = json.load(f)
    except:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Erro ao ler arquivo de cotações"}
        )

    cotacao = None
    for c in cotacoes:
        if c.get("numero_cotacao") == numero_cotacao:
            cotacao = c
            break

    if not cotacao:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": f"Cotação {numero_cotacao} não encontrada"}
        )

    return {
        "success": True,
        "message": "Recibo gerado com sucesso",
        "dados": cotacao
    }


@router.get("/ultimas-cotacoes")
async def ultimas_cotacoes(limite: int = 10):
    """Retorna as últimas cotações"""
    cotacoes_file = "cotacoes.json"

    if not os.path.exists(cotacoes_file):
        return {"success": True, "dados": []}

    try:
        with open(cotacoes_file, "r") as f:
            cotacoes = json.load(f)
    except:
        return {"success": True, "dados": []}

    # Retornar as últimas
    ultimas = cotacoes[-limite:] if len(cotacoes) > limite else cotacoes
    ultimas.reverse()

    return {"success": True, "dados": ultimas}