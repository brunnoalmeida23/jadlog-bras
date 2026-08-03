from __future__ import annotations

import os

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(tags=["Autenticação"])

templates_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "templates",
)

templates = Jinja2Templates(directory=templates_dir)


@router.get("/login", response_class=HTMLResponse)
async def pagina_login(request: Request):
    if request.session.get("autenticado"):
        return RedirectResponse(
            url="/simulador/",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "erro": None,
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def realizar_login(
    request: Request,
    senha: str = Form(...),
):
    senha_correta = os.getenv(
        "FUNCIONARIO_SENHA",
        "JadLog2026",
    )

    if senha != senha_correta:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "erro": "Senha incorreta.",
            },
            status_code=401,
        )

    request.session.clear()
    request.session["autenticado"] = True

    return RedirectResponse(
        url="/simulador/",
        status_code=303,
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()

    resposta = RedirectResponse(
        url="/login",
        status_code=303,
    )

    resposta.delete_cookie("jadlog_session")
    return resposta
