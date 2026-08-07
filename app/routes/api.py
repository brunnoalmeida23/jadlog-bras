# app/routes/api.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.frete_calculator import FreteCalculator

router = APIRouter(prefix="/api", tags=["API"])

# Instância do calculador (criada uma vez e reutilizada)
calculadora = FreteCalculator()


@router.get("/calcular-frete")
async def calcular_frete(
    cep: str,
    peso: float,
    modalidade: str = "PACKAGE",
    valor_nf: float = 0.0
):
    """
    Calcula o frete com base no CEP, peso, modalidade e valor da NF.
    """
    try:
        resultado = calculadora.calcular(cep, peso, modalidade, valor_nf)
        return JSONResponse(content=resultado)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "erro": str(e)}
        )


# ============================================================
# ROTA ADICIONAL PARA COMPATIBILIDADE COM O FRONTEND
# ============================================================
@router.get("/simular")
async def simular_frete(
    cep: str,
    peso: float,
    modalidade: str = "PACKAGE",
    valor_nf: float = 0.0
):
    """
    Rota alternativa que chama a função calcular_frete.
    Mantida para compatibilidade com o frontend.
    """
    return await calcular_frete(cep, peso, modalidade, valor_nf)

# ============================================================
# ROTAS DE CONSULTA
# ============================================================

from app.routes.consulta import buscar_cotacao_por_numero, salvar_cotacao

@router.get("/cotacao/buscar")
async def buscar_cotacao(numero: str):
    """Busca uma cotação pelo número"""
    cotacao = buscar_cotacao_por_numero(numero)
    if cotacao:
        return {"encontrado": True, "cotacao": cotacao}
    return {"encontrado": False, "cotacao": None}

@router.post("/cotacao/salvar")
async def salvar_cotacao_endpoint(dados: dict):
    """Salva uma cotação"""
    resultado = salvar_cotacao(dados)
    if resultado:
        return {"success": True, "cotacao": resultado}
    return {"success": False, "message": "Erro ao salvar cotação"}