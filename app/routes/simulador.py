from __future__ import annotations

import os
import re

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.api_frete_externa import (
    ErroApiFrete,
    consultar_frete,
)
from app.services.cep_service import CEPService
from app.utils.helpers import gerar_cotacao_id


router = APIRouter(
    prefix="/simulador",
    tags=["Simulador"],
)

templates_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "templates",
)

templates = Jinja2Templates(directory=templates_dir)
cep_service = CEPService()


@router.get("/", response_class=HTMLResponse)
async def simulador_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="simulador.html",
        context={},
    )


@router.post("/calcular")
async def calcular_frete(
    cep_destino: str = Form(...),
    peso: float = Form(...),
    valor_nf: float = Form(0.0),
    volumes: int = Form(1),
    cliente_nome: str = Form("Cliente não informado"),
    cliente_documento: str = Form(""),
):
    cep_limpo = re.sub(r"\D", "", cep_destino)

    if len(cep_limpo) != 8:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "CEP inválido. Digite exatamente 8 números.",
            },
        )

    if peso <= 0:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "O peso deve ser maior que zero.",
            },
        )

    if valor_nf < 0:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "O valor da NF não pode ser negativo.",
            },
        )

    if volumes <= 0:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "A quantidade de volumes deve ser maior que zero.",
            },
        )

    info_cep = cep_service.buscar(cep_limpo)

    if not info_cep:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "CEP não encontrado na base de atendimento.",
            },
        )

    try:
        frete = await consultar_frete(
            cep_destino=cep_limpo,
            peso=peso,
            valor_nf=valor_nf,
        )

    except ErroApiFrete as erro:
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "message": str(erro),
            },
        )

    numero_cotacao = gerar_cotacao_id()

    cidade = str(info_cep.get("cidade", "")).strip()
    uf = str(info_cep.get("uf", "")).strip()
    tipo_tarifa = str(
        info_cep.get("tipo_tarifa", "")
    ).strip()

    prazo = info_cep.get("prazo", 5)

    return {
        "success": True,
        "dados": {
            "numero_cotacao": numero_cotacao,
            "cep": cep_limpo,
            "destino": f"{cidade}/{uf}",
            "cidade": cidade,
            "uf": uf,
            "tipo": tipo_tarifa,
            "prazo": f"{prazo} dias úteis",
            "prazo_dias": prazo,
            "peso": peso,
            "volumes": volumes,
            "valor_nf": valor_nf,
            "package": frete["package"],
            "com": frete["com"],
            "cliente_nome": cliente_nome,
            "cliente_documento": cliente_documento,
            "fonte": "VOCE_QUEM_MANDA",
        },
    }