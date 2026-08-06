# app/routes/rastreio.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.services.sessao import sessoes

# ============================================================
# CRIAÇÃO DO ROUTER - OBRIGATÓRIO!
# ============================================================
router = APIRouter(prefix="/rastreio", tags=["Rastreio"])

# ============================================================
# ROTA PRINCIPAL DA PÁGINA DE RASTREIO
# ============================================================
@router.get("/", response_class=HTMLResponse)
async def rastreio_page(request: Request):
    token = request.cookies.get("auth_token")
    logado = token and token in sessoes
    botao_menu = '<a class="nav-link" href="/logout">Sair</a>' if logado else '<a class="nav-link login-btn" href="/login">Login</a>'
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Rastreio | JADLOG BRÁS</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        .bg-jadlog {{ background: #E31E24; }}
        .btn-jadlog {{ background: #E31E24; color: white; border: none; padding: 10px 30px; border-radius: 8px; }}
        .btn-jadlog:hover {{ background: #B81217; color: white; }}
        .card-shadow {{ background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); padding: 24px; }}
        .footer {{ background: #212529; color: white; padding: 15px 0; margin-top: 40px; text-align: center; }}
        .nav-link {{ color: white !important; }}
        .navbar-brand {{ color: white !important; font-weight: 700; display: flex; align-items: center; gap: 10px; text-decoration: none; }}
        .logo-img {{ height: 55px; background: white; padding: 5px 15px; border-radius: 60px; }}
        .nav-link.login-btn {{ background: white; color: #E31E24 !important; padding: 5px 20px; border-radius: 20px; font-weight: 600; }}
        .nav-link.login-btn:hover {{ background: #f0f0f0; }}
        .brand-text {{ color: white; font-size: 1.3rem; font-weight: 700; margin-left: 5px; }}
        
        .search-box {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            text-align: center;
        }}
        
        .search-box h2 {{
            color: #E31E24;
            margin-bottom: 20px;
        }}
        
        .search-box .input-group {{
            max-width: 500px;
            margin: 0 auto;
        }}
        
        .evento-item {{
            border-left: 4px solid #E31E24;
            margin-bottom: 15px;
            padding: 12px 20px;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
            transition: all 0.3s;
        }}
        
        .evento-item:hover {{
            background: #f0f0f0;
            transform: translateX(5px);
        }}
        
        .evento-item .data-hora {{
            font-size: 0.85rem;
            color: #6c757d;
            font-weight: 600;
        }}
        
        .evento-item .status {{
            font-size: 1rem;
            font-weight: 500;
            color: #212529;
        }}
        
        .status-entregue {{ color: #28a745; }}
        .status-coletado {{ color: #17a2b8; }}
        .status-caminho {{ color: #0d6efd; }}
        
        .badge-entregue {{ background: #28a745; color: white; padding: 6px 14px; border-radius: 20px; }}
        .badge-transito {{ background: #ffc107; color: #212529; padding: 6px 14px; border-radius: 20px; }}
        .badge-coletado {{ background: #17a2b8; color: white; padding: 6px 14px; border-radius: 20px; }}
        .badge-caminho {{ background: #0d6efd; color: white; padding: 6px 14px; border-radius: 20px; }}
        
        .remessa-info {{
            background: #e9ecef;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        
        .loading {{
            text-align: center;
            padding: 30px;
        }}
        
        .loading .spinner {{
            animation: spin 1s linear infinite;
            font-size: 2rem;
        }}
        
        @keyframes spin {{
            100% {{ transform: rotate(360deg); }}
        }}
        
        .search-icon {{
            font-size: 3rem;
            color: #E31E24;
            margin-bottom: 15px;
        }}
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
                    <li class="nav-item">
                        {botao_menu}
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container py-4">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                <div class="search-box">
                    <div class="search-icon">
                        <i class="bi bi-box-seam"></i>
                    </div>
                    <h2>RASTREIE SUA ENCOMENDA</h2>
                    <p class="text-muted">Digite o código de rastreio para acompanhar sua encomenda</p>
                    
                    <div class="input-group">
                        <input type="text" class="form-control form-control-lg" 
                               placeholder="Ex: 18137200312411" id="codigoRastreio" 
                               onkeypress="if(event.key==='Enter') buscarRastreio()">
                        <button class="btn btn-jadlog btn-lg" onclick="buscarRastreio()">
                            <i class="bi bi-search"></i> Procurar
                        </button>
                    </div>
                    <div id="resultado" class="mt-4"></div>
                </div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">&copy; 2026 JADLOG BRÁS</div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // ============================================================
        // CONFIGURAÇÃO DA URL DA API
        // ============================================================
        const API_URL = 'https://jadlog-api.onrender.com';  // API de rastreio na porta 8001
        
        function buscarRastreio() {{
            const codigo = document.getElementById('codigoRastreio').value.trim();
            const resultado = document.getElementById('resultado');
            
            if (!codigo) {{
                resultado.innerHTML = '<div class="alert alert-warning">Digite um código de rastreio.</div>';
                return;
            }}
            
            resultado.innerHTML = `
                <div class="loading">
                    <div class="spinner">⏳</div>
                    <p class="mt-2">Buscando rastreio para o código ${{codigo}}...</p>
                    <small class="text-muted">Isso pode levar alguns segundos</small>
                </div>
            `;
            
            fetch(`${{API_URL}}/rastreio/${{encodeURIComponent(codigo)}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        exibirResultado(data);
                    }} else {{
                        resultado.innerHTML = `<div class="alert alert-danger">${{data.message || 'Erro ao buscar rastreio'}}</div>`;
                    }}
                }})
                .catch(error => {{
                    console.error('Erro:', error);
                    resultado.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="bi bi-exclamation-triangle"></i>
                            Serviço de rastreio temporariamente indisponível.<br>
                            <small>Verifique se a API está rodando em ${{API_URL}}</small>
                        </div>
                    `;
                }});
        }}
        
        function exibirResultado(data) {{
            const resultado = document.getElementById('resultado');
            
            let badgeClass = 'badge-transito';
            let statusText = 'Em trânsito';
            let statusIcon = 'bi-truck';
            
            if (data.status === 'Entregue') {{
                badgeClass = 'badge-entregue';
                statusText = 'Entregue';
                statusIcon = 'bi-check-circle';
            }} else if (data.status === 'Coletado') {{
                badgeClass = 'badge-coletado';
                statusText = 'Coletado';
                statusIcon = 'bi-box';
            }} else if (data.status === 'Saiu para entrega') {{
                badgeClass = 'badge-caminho';
                statusText = 'Saiu para entrega';
                statusIcon = 'bi-truck-front';
            }}
            
            let html = `
                <div class="card card-shadow mt-3 text-start">
                    <h5 class="text-center mb-3" style="color: #E31E24;">
                        <i class="bi bi-box-seam"></i> RASTREAMENTO DE ENCOMENDA
                    </h5>
                    
                    <div class="remessa-info">
                        <strong>Resultados da busca</strong><br>
                        <span class="text-muted">Status referente à consulta: </span>
                        <strong>${{data.codigo}}</strong>
                    </div>
            `;
            
            if (data.remessa) {{
                html += `
                    <div class="remessa-info">
                        <strong>Remessa</strong><br>
                        <span style="font-size: 1.1rem; font-weight: 600;">${{data.remessa}}</span>
                    </div>
                `;
            }}
            
            html += `
                <div class="mt-2 mb-3">
                    <span class="${{badgeClass}} fs-6">
                        <i class="bi ${{statusIcon}}"></i> ${{statusText}}
                    </span>
                </div>
                <hr>
            `;
            
            if (data.historico && data.historico.length > 0) {{
                data.historico.forEach(evento => {{
                    let classe = '';
                    let icon = 'bi-dot';
                    
                    if (evento.status && evento.status.toLowerCase().includes('entregue')) {{
                        classe = 'status-entregue';
                        icon = 'bi-check-circle';
                    }} else if (evento.status && evento.status.toLowerCase().includes('coletado')) {{
                        classe = 'status-coletado';
                        icon = 'bi-box';
                    }} else if (evento.status && evento.status.toLowerCase().includes('caminho')) {{
                        classe = 'status-caminho';
                        icon = 'bi-truck';
                    }}
                    
                    html += `
                        <div class="evento-item">
                            <div class="data-hora">
                                <i class="bi bi-clock"></i> ${{evento.data || ''}} - ${{evento.hora || ''}}
                            </div>
                            <div class="status ${{classe}}">
                                <i class="bi ${{icon}} me-1"></i>
                                ${{evento.status || 'Evento'}}
                            </div>
                        </div>
                    `;
                }});
            }} else {{
                html += `<div class="text-muted text-center">Nenhum evento encontrado.</div>`;
            }}
            
            html += `</div>`;
            resultado.innerHTML = html;
            
            resultado.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
    </script>
</body>
</html>
    """