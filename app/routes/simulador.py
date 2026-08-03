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
from app.services.comissao_service import (
    ErroComissao,
    aplicar_comissao,
)
from app.utils.helpers import gerar_cotacao_id


router = APIRouter(
    prefix="/simulador",
    tags=["Simulador"],
)

templates_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "templates",
)

templates = Jinja2Templates(
    directory=templates_dir
)

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
    valor_nf: float = Form(...),
    volumes: int = Form(1),
    cliente_nome: str = Form(
        "Cliente não informado"
    ),
    cliente_documento: str = Form(""),
):
    cep_limpo = re.sub(
        r"\D",
        "",
        str(cep_destino),
    )

    if len(cep_limpo) != 8:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": (
                    "CEP inválido. Digite 8 números."
                ),
            },
        )

    if peso <= 0:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": (
                    "O peso deve ser maior que zero."
                ),
            },
        )

    if valor_nf < 0:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": (
                    "O valor da nota não pode ser negativo."
                ),
            },
        )

    if volumes <= 0:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": (
                    "Volumes deve ser maior que zero."
                ),
            },
        )

    info_cep = cep_service.buscar(cep_limpo)

    if not info_cep:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": (
                    "CEP não localizado na base tarifária."
                ),
            },
        )

    uf = str(
        info_cep.get("uf", "")
    ).strip().upper()

    tipo_tarifa = str(
        info_cep.get("tipo_tarifa", "")
    ).strip()

    if not uf or not tipo_tarifa:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": (
                    "O CEP não possui UF ou tabela "
                    "tarifária válida."
                ),
            },
        )

    try:
        frete_api = await consultar_frete(
            cep_destino=cep_limpo,
            peso=peso,
            valor_nf=valor_nf,
        )

        package = aplicar_comissao(
            valor_api=frete_api["package"],
            modalidade="PACKAGE",
            tipo_tarifa=tipo_tarifa,
            uf=uf,
            peso=peso,
        )

        com = aplicar_comissao(
            valor_api=frete_api["com"],
            modalidade=".COM",
            tipo_tarifa=tipo_tarifa,
            uf=uf,
            peso=peso,
        )

    except ErroApiFrete as erro:
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "message": str(erro),
            },
        )

    except ErroComissao as erro:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": (
                    f"Erro na comissão: {erro}"
                ),
            },
        )

    numero_cotacao = gerar_cotacao_id()

    cidade = str(
        info_cep.get("cidade", "")
    ).strip()

    return {
        "success": True,
        "dados": {
            "numero_cotacao": numero_cotacao,
            "cep": cep_limpo,
            "destino": f"{cidade}/{uf}",
            "cidade": cidade,
            "uf": uf,
            "tipo": tipo_tarifa,
            "prazo": info_cep.get("prazo"),
            "peso": peso,
            "volumes": volumes,
            "valor_nf": valor_nf,

            # Estes dois campos continuam sendo usados
            # pela tela, PDF e impressão.
            # Agora já contêm API + comissão.
            "package": package["valor_final"],
            "com": com["valor_final"],

            # Detalhamento interno para auditoria.
            "package_base": package["valor_api"],
            "package_comissao": package["comissao"],
            "com_base": com["valor_api"],
            "com_comissao": com["comissao"],

            "cliente_nome": cliente_nome,
            "cliente_documento": cliente_documento,
        },
    }