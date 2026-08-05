# app/routes/home.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(prefix="", tags=["Home"])

# Configuração dos templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

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