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


def _cabecalhos_sem_cache() -> dict[str, str]:
    return {
        "Cache-Control": (
            "no-store, no-cache, must-revalidate, max-age=0"
        ),
        "Pragma": "no-cache",
        "Expires": "0",
    }


@router.get("/login", response_class=HTMLResponse)
async def pagina_login(request: Request):
    if request.session.get("autenticado"):
        return RedirectResponse(
            url="/simulador/",
            status_code=303,
            headers=_cabecalhos_sem_cache(),
        )

    resposta = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "erro": None,
        },
    )

    resposta.headers.update(_cabecalhos_sem_cache())

    return resposta


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
        resposta = templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "erro": "Senha incorreta.",
            },
            status_code=401,
        )

        resposta.headers.update(_cabecalhos_sem_cache())

        return resposta

    request.session.clear()
    request.session["autenticado"] = True

    return RedirectResponse(
        url="/simulador/",
        status_code=303,
        headers=_cabecalhos_sem_cache(),
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()

    resposta = RedirectResponse(
        url="/login",
        status_code=303,
        headers=_cabecalhos_sem_cache(),
    )

    resposta.delete_cookie(
        key="jadlog_session",
        path="/",
        secure=os.getenv("VERCEL") == "1",
        httponly=True,
        samesite="lax",
    )

    return resposta