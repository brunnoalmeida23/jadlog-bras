from __future__ import annotations

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from app.services.frete_calculator import FreteCalculator
from app.services.supabase_service import SupabaseConfigError, get_supabase_service

router = APIRouter(prefix="/api", tags=["API"])
calculadora = FreteCalculator()


def _erro_supabase(exc: Exception) -> JSONResponse:
    if isinstance(exc, SupabaseConfigError):
        return JSONResponse(
            status_code=503,
            content={"success": False, "erro": str(exc), "codigo": "SUPABASE_CONFIG"},
        )
    return JSONResponse(
        status_code=502,
        content={"success": False, "erro": f"Falha ao acessar o banco: {exc}"},
    )


@router.get("/calcular-frete")
async def calcular_frete(
    cep: str,
    peso: float,
    modalidade: str = "PACKAGE",
    valor_nf: float = 0.0,
):
    try:
        resultado = calculadora.calcular(cep, peso, modalidade, valor_nf)
        return JSONResponse(content=resultado)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "erro": str(exc)})


@router.get("/simular")
async def simular_frete(
    cep: str,
    peso: float,
    modalidade: str = "PACKAGE",
    valor_nf: float = 0.0,
):
    return await calcular_frete(cep, peso, modalidade, valor_nf)


@router.get("/supabase/status")
async def supabase_status():
    try:
        service = get_supabase_service()
        service._request("GET", "clientes", params={"select": "id", "limit": "1"})
        return {"success": True, "configured": True, "connected": True}
    except Exception as exc:
        return _erro_supabase(exc)


@router.post("/buscar-cliente")
async def buscar_cliente(termo: str = Form(...)):
    try:
        cliente = get_supabase_service().buscar_cliente_por_cpf(termo)
        if cliente:
            return {"success": True, "dados": [cliente], "quantidade": 1}
        return {"success": False, "dados": [], "message": "Cliente não encontrado."}
    except Exception as exc:
        return _erro_supabase(exc)


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
    try:
        service = get_supabase_service()
        existente = service.buscar_cliente_por_cpf(cpf_cnpj)
        if existente:
            return JSONResponse(
                status_code=409,
                content={"success": False, "message": "CPF ou CNPJ já cadastrado.", "dados": existente},
            )
        dados = {
            "cpf_cnpj": service.somente_numeros(cpf_cnpj),
            "nome": nome.strip(),
            "razao_social": razao_social.strip(),
            "endereco": endereco.strip(),
            "cidade": cidade.strip(),
            "uf": uf.strip().upper(),
            "cep": service.somente_numeros(cep),
            "telefone": telefone.strip(),
        }
        cliente = service.cadastrar_cliente(dados)
        return {"success": True, "dados": cliente, "message": "Cliente cadastrado com sucesso."}
    except Exception as exc:
        return _erro_supabase(exc)


@router.get("/cotacao/buscar")
async def buscar_cotacao(numero: str):
    try:
        cotacao = get_supabase_service().buscar_cotacao_por_numero(numero)
        return {"encontrado": bool(cotacao), "cotacao": cotacao}
    except Exception as exc:
        return _erro_supabase(exc)


@router.post("/cotacao/salvar")
async def salvar_cotacao_endpoint(dados: dict):
    try:
        cotacao = get_supabase_service().salvar_cotacao(dados)
        if cotacao:
            return {"success": True, "cotacao": cotacao}
        return JSONResponse(status_code=500, content={"success": False, "message": "Supabase não retornou a cotação salva."})
    except Exception as exc:
        return _erro_supabase(exc)
