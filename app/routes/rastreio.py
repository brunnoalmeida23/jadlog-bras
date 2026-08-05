# app/routes/rastreio.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import re
import requests
from bs4 import BeautifulSoup

router = APIRouter(prefix="/rastreio", tags=["Rastreio"])

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def rastreio_page(request: Request):
    """Página de rastreio"""
    return templates.TemplateResponse("rastreio.html", {"request": request})


@router.post("/buscar")
async def buscar_rastreio(codigo: str = Form(...)):
    """Busca rastreio no site da Jadlog"""
    try:
        url = "https://www.jadlog.com.br/tracking/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9',
        }
        
        dados = {'cte': codigo}
        
        response = requests.post(url, data=dados, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Erro ao acessar o site da Jadlog"}
            )
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar eventos
        eventos = []
        status_atual = "Em trânsito"
        
        # Procurar a tabela de rastreio
        tabela = soup.find('table')
        if tabela:
            linhas = tabela.find_all('tr')
            for linha in linhas:
                colunas = linha.find_all('td')
                if len(colunas) >= 3:
                    texto = linha.get_text(strip=True)
                    if 'entregue' in texto.lower():
                        status_atual = "Entregue"
                    elif 'coletado' in texto.lower():
                        status_atual = "Coletado"
                    elif 'transferência' in texto.lower() or 'caminho' in texto.lower():
                        status_atual = "Em trânsito"
        
        # Buscar divs com eventos
        divs = soup.find_all('div', class_=re.compile(r'event|track|status|timeline'))
        for div in divs:
            texto = div.get_text(strip=True)
            if texto and any(p in texto.lower() for p in ['entregue', 'coletado', 'transferência', 'caminho', 'saiu', 'chegou']):
                data_match = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
                hora_match = re.search(r'(\d{2}:\d{2})', texto)
                if data_match:
                    eventos.append({
                        'data': data_match.group(1),
                        'hora': hora_match.group(1) if hora_match else '',
                        'status': texto[:150],
                        'local': ''
                    })
        
        if not eventos:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": f"Nenhum evento encontrado para o código {codigo}"}
            )
        
        return {
            "success": True,
            "codigo": codigo,
            "status": status_atual,
            "historico": eventos
        }
        
    except requests.exceptions.Timeout:
        return JSONResponse(
            status_code=504,
            content={"success": False, "message": "Tempo limite excedido. Tente novamente."}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Erro ao buscar rastreio: {str(e)}"}
        )