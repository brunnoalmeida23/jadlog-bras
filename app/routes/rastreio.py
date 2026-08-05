# app/routes/rastreio.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
import requests
from bs4 import BeautifulSoup
import re

router = APIRouter(prefix="/rastreio", tags=["Rastreio"])

@router.get("/", response_class=HTMLResponse)
async def rastreio_page(request: Request):
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Rastreio | JADLOG BRÁS</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        .bg-jadlog { background: #E31E24; }
        .btn-jadlog { background: #E31E24; color: white; border: none; padding: 10px 30px; border-radius: 8px; }
        .btn-jadlog:hover { background: #B81217; color: white; }
        .card-shadow { background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); padding: 24px; }
        .footer { background: #212529; color: white; padding: 15px 0; margin-top: 40px; text-align: center; }
        .nav-link { color: white !important; }
        .navbar-brand { color: white !important; font-weight: 700; display: flex; align-items: center; gap: 10px; text-decoration: none; }
        .logo-img { height: 55px; background: white; padding: 5px 15px; border-radius: 60px; }
        .nav-link.login-btn { background: white; color: #E31E24 !important; padding: 5px 20px; border-radius: 20px; font-weight: 600; }
        .nav-link.login-btn:hover { background: #f0f0f0; }
        .brand-text { color: white; font-size: 1.3rem; font-weight: 700; margin-left: 5px; }
        .evento-item { 
            border-left: 4px solid #E31E24; 
            margin-bottom: 15px; 
            padding: 10px 15px; 
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
        }
        .evento-item .data { font-size: 0.85rem; color: #6c757d; font-weight: 600; }
        .evento-item .status { font-weight: 600; font-size: 1rem; }
        .evento-item .remessa { font-size: 0.85rem; color: #495057; }
        .status-entregue { color: #28a745; }
        .status-transito { color: #ffc107; }
        .status-coletado { color: #17a2b8; }
        .loading { text-align: center; padding: 30px; }
        .loading .spinner { animation: spin 1s linear infinite; font-size: 2rem; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        .card-resultado { background: #fff; border-radius: 12px; padding: 20px; margin-top: 20px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg bg-jadlog">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/img/logo-jadlog.png" alt="JADLOG BRÁS" class="logo-img">
                <span class="brand-text">JADLOG BRÁS</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMenu">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Início</a></li>
                    <li class="nav-item"><a class="nav-link" href="/simulador">Simulador</a></li>
                    <li class="nav-item"><a class="nav-link" href="/consulta">Consulta</a></li>
                    <li class="nav-item"><a class="nav-link" href="/rastreio">Rastreio</a></li>
                    <li class="nav-item"><a class="nav-link login-btn" href="/login">Login</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container py-4">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                <h2 class="text-center mb-4" style="color: #E31E24;">
                    <i class="bi bi-box-seam"></i> Rastreio de Encomendas
                </h2>
                
                <div class="card card-shadow">
                    <div class="card-body">
                        <p class="text-muted text-center">
                            Digite o código de rastreio (CNPJ ou Remessa) para acompanhar sua encomenda.
                        </p>
                        <div class="row g-3">
                            <div class="col-md-8 mx-auto">
                                <div class="input-group">
                                    <input type="text" class="form-control form-control-lg" 
                                           placeholder="Ex: 18137200312411" id="codigoRastreio">
                                    <button class="btn btn-jadlog btn-lg" onclick="buscarRastreio()">
                                        <i class="bi bi-search"></i> Rastrear
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div id="resultado" class="mt-4"></div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">&copy; 2026 JADLOG BRÁS</div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function buscarRastreio() {
            const codigo = document.getElementById('codigoRastreio').value.trim();
            const resultado = document.getElementById('resultado');
            
            if (!codigo) {
                resultado.innerHTML = '<div class="alert alert-warning">Digite um código de rastreio.</div>';
                return;
            }
            
            resultado.innerHTML = `
                <div class="loading">
                    <div class="spinner">⏳</div>
                    <p class="mt-2">Buscando rastreio para o código ${codigo}...</p>
                </div>
            `;
            
            fetch(`/rastreio/buscar?codigo=${encodeURIComponent(codigo)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        exibirResultado(data);
                    } else {
                        resultado.innerHTML = `<div class="alert alert-danger">${data.message || 'Erro ao buscar rastreio'}</div>`;
                    }
                })
                .catch(() => {
                    resultado.innerHTML = `<div class="alert alert-danger">Erro ao buscar rastreio. Tente novamente.</div>`;
                });
        }
        
        function exibirResultado(data) {
            const resultado = document.getElementById('resultado');
            
            let statusClass = 'status-transito';
            let statusText = 'Em trânsito';
            
            if (data.status && data.status.toLowerCase().includes('entregue')) {
                statusClass = 'status-entregue';
                statusText = 'Entregue';
            } else if (data.status && data.status.toLowerCase().includes('coletado')) {
                statusClass = 'status-coletado';
                statusText = 'Coletado';
            }
            
            let html = `
                <div class="card card-resultado">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0"><i class="bi bi-box"></i> Código: <strong>${data.codigo}</strong></h5>
                        <span class="badge ${statusClass} fs-6">${statusText}</span>
                    </div>
                    ${data.remessa ? `<p class="text-muted small">Remessa: ${data.remessa}</p>` : ''}
                    <hr>
                    <div class="timeline">
            `;
            
            if (data.historico && data.historico.length > 0) {
                data.historico.forEach(evento => {
                    let classe = '';
                    if (evento.status && evento.status.toLowerCase().includes('entregue')) {
                        classe = 'status-entregue';
                    } else if (evento.status && evento.status.toLowerCase().includes('coletado')) {
                        classe = 'status-coletado';
                    }
                    
                    html += `
                        <div class="evento-item">
                            <div class="data">${evento.data || ''} ${evento.hora || ''}</div>
                            <div class="status ${classe}">${evento.status || 'Evento'}</div>
                            ${evento.local ? `<div class="text-muted small">${evento.local}</div>` : ''}
                        </div>
                    `;
                });
            } else {
                html += `<div class="text-muted">Nenhum evento encontrado.</div>`;
            }
            
            html += `
                    </div>
                </div>
            `;
            resultado.innerHTML = html;
        }
    </script>
</body>
</html>
    """

@router.get("/buscar")
async def buscar_rastreio(codigo: str):
    """Busca o rastreio no site da Jadlog"""
    try:
        url = "https://www.jadlog.com.br/jadlog/rastreio"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
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
        remessa = ""
        
        # Buscar remessa
        remessa_elem = soup.find(string=re.compile(r'Remessa'))
        if remessa_elem:
            remessa_text = remessa_elem.parent.get_text(strip=True) if remessa_elem.parent else remessa_elem
            remessa_match = re.search(r'Remessa\s*[\n\r]*\s*(\d+)', remessa_text)
            if remessa_match:
                remessa = remessa_match.group(1)
        
        # Buscar todos os blocos de eventos
        # O site da Jadlog lista eventos em ordem cronológica
        eventos_blocos = soup.find_all(['div', 'p', 'li'], class_=re.compile(r'event|status|track|row|item|result|list', re.I))
        
        # Se não encontrar por classe, busca por padrão de data
        if not eventos_blocos:
            textos = soup.find_all(text=re.compile(r'\d{2}/\d{2}/\d{4}'))
            for texto in textos:
                data_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})?', texto)
                if data_match:
                    parent = texto.parent
                    status_text = parent.get_text(strip=True) if parent else texto
                    # Remove a data do status
                    status_text = re.sub(r'\d{2}/\d{2}/\d{4}\s*-\s*\d{2}:\d{2}\s*', '', status_text).strip()
                    eventos.append({
                        'data': data_match.group(1),
                        'hora': data_match.group(2) if data_match.group(2) else '',
                        'status': status_text,
                        'local': ''
                    })
        
        # Se não encontrou, tenta outra abordagem
        if not eventos:
            # Busca por elementos que contêm data
            elementos = soup.find_all(['div', 'p', 'li', 'span'])
            for el in elementos:
                texto = el.get_text(strip=True)
                data_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})', texto)
                if data_match:
                    status_text = re.sub(r'\d{2}/\d{2}/\d{4}\s*-\s*\d{2}:\d{2}\s*', '', texto).strip()
                    if status_text:
                        eventos.append({
                            'data': data_match.group(1),
                            'hora': data_match.group(2),
                            'status': status_text[:200],
                            'local': ''
                        })
        
        # Atualiza status baseado no último evento
        if eventos:
            ultimo_status = eventos[-1]['status'].lower()
            if 'entregue' in ultimo_status or 'entregue' in eventos[-1]['status']:
                status_atual = "Entregue"
            elif 'coletado' in ultimo_status:
                status_atual = "Coletado"
            elif 'transferência' in ultimo_status or 'caminho' in ultimo_status:
                status_atual = "Em trânsito"
        
        if not eventos:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": f"Nenhum evento encontrado para o código {codigo}. Verifique se o código está correto."}
            )
        
        return {
            "success": True,
            "codigo": codigo,
            "remessa": remessa,
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
            content={"success": False, "message": f"Erro ao buscar rastreio: {str(e)}" if str(e) else "Erro inesperado ao buscar rastreio. Tente novamente."}
        )