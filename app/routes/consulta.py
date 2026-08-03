from __future__ import annotations

import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/consulta",
    tags=["Consulta"],
)

templates_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "templates",
)

templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def consulta_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="consulta.html",
        context={},
    )