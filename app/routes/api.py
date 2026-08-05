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