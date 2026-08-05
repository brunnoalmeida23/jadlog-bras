# app/routes/home.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(prefix="", tags=["Home"])

# Caminho SIMPLES dos templates (funciona na Vercel)
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/home", response_class=HTMLResponse)
async def home_redirect():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>JADLOG BRÁS</title>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=/">
</head>
<body>
    <p>Redirecionando para <a href="/">página inicial</a>...</p>
</body>
</html>
    """