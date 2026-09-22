# app/routes/simulador.py

from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.frete_calculator import FreteCalculator


router = APIRouter(prefix="/simulador", tags=["Simulador"])

templates = Jinja2Templates(directory="app/templates")

calculadora = FreteCalculator()


@router.get("/", response_class=HTMLResponse)
async def simulador_page(request: Request):
    return templates.TemplateResponse(
        "simulador.html",
        {
            "request": request,
            "session": request.session,
        },
    )


@router.post("/calcular")
async def calcular_simulador(
    request: Request,
    cep_destino: str = Form(...),
    peso: float = Form(...),
    volumes: int = Form(1),
    valor_nf: float = Form(0.0),
    cliente_nome: str = Form(""),
    cliente_documento: str = Form(""),
):
    try:
        cep = "".join(filter(str.isdigit, cep_destino))

        if len(cep) != 8:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "erro": "Informe um CEP válido com 8 dígitos.",
                },
            )

        if peso <= 0:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "erro": "Informe um peso maior que zero.",
                },
            )

        if volumes <= 0:
            volumes = 1

        if valor_nf < 0:
            valor_nf = 0.0

        # Calcula PACKAGE
        resultado_package = calculadora.calcular(
            cep=cep,
            peso=peso,
            modalidade="PACKAGE",
            valor_nf=valor_nf,
        )

        if resultado_package.get("erro"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "erro": resultado_package["erro"],
                },
            )

        # Calcula .COM
        resultado_com = calculadora.calcular(
            cep=cep,
            peso=peso,
            modalidade=".COM",
            valor_nf=valor_nf,
        )

        if resultado_com.get("erro"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "erro": resultado_com["erro"],
                },
            )

        dados_package = resultado_package["dados"]
        dados_com = resultado_com["dados"]

        agora = datetime.now()

        numero_cotacao = (
            f"COT-{agora.year}-"
            f"{agora.month:02d}{agora.day:02d}-"
            f"{agora.hour:02d}{agora.minute:02d}"
        )

        dados = {
            "numero_cotacao": numero_cotacao,
            "cep": cep,
            "uf": dados_package.get("uf", ""),
            "cidade": dados_package.get("cidade", ""),
            "destino": (
                f"{dados_package.get('cidade', '')}"
                f"/{dados_package.get('uf', '')}"
            ).strip("/"),
            "tipo_tarifa": dados_package.get("tipo_tarifa", ""),
            "prazo": dados_package.get("prazo", ""),
            "peso": peso,
            "volumes": volumes,
            "valor_nf": valor_nf,
            "cliente_nome": cliente_nome.strip(),
            "cliente_documento": cliente_documento.strip(),
            "package": dados_package.get("total", 0),
            "com": dados_com.get("total", 0),
        }

        return {
            "success": True,
            "dados": dados,
        }

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "erro": str(exc),
            },
        )
