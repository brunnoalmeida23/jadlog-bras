# app/routes/simulador.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import re

from app.services.frete_calculator import FreteCalculator
from app.utils.helpers import gerar_cotacao_id

router = APIRouter(prefix="/simulador", tags=["Simulador"])

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def simulador_page(request: Request):
    """Página do simulador"""
    return templates.TemplateResponse("simulador.html", {"request": request})


@router.post("/calcular")
async def calcular_frete(
    cep_destino: str = Form(...),
    peso: float = Form(...),
    modalidade: str = Form("PACKAGE"),
    valor_nf: float = Form(0.0),
    cliente_nome: str = Form("Cliente não informado"),
    cliente_documento: str = Form("")
):
    """Calcula o frete usando a regra completa"""
    calculator = FreteCalculator()

    # Limpar CEP
    cep_limpo = re.sub(r'\D', '', cep_destino)
    if len(cep_limpo) != 8:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "CEP inválido. Digite 8 dígitos."}
        )

    if peso <= 0:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Peso deve ser maior que zero."}
        )

    # Calcular frete
    resultado = calculator.calcular(cep_limpo, peso, modalidade, valor_nf)

    if "erro" in resultado:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": resultado["erro"]}
        )

    # Gerar número da cotação
    numero_cotacao = gerar_cotacao_id()

    # Dados do resultado
    d = resultado["dados"]

    return {
        "success": True,
        "dados": {
            "numero_cotacao": numero_cotacao,
            "destino": f"{d['cidade']}/{d['uf']}",
            "tipo": d["tipo_tarifa"],
            "regiao": d["regiao"],
            "prazo": f"{d['prazo']} dias úteis",
            "peso": f"{peso:.3f} kg",
            "modalidade": modalidade,
            "glm": d["glm"],
            "lucro_cliente": d["lucro_cliente"],
            "valor_base": d["final"],
            "seguro": d["ad_valorem"],
            "total": d["total"],
            "cliente_nome": cliente_nome,
            "cliente_documento": cliente_documento
        }
    }