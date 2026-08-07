# app/routes/consulta.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.services.sessao import sessoes

router = APIRouter(prefix="/consulta", tags=["Consulta"])

@router.get("/", response_class=HTMLResponse)
async def consulta_page(request: Request):
    token = request.cookies.get("auth_token")
    logado = token and token in sessoes
    
    botao_menu = '<a class="nav-link" href="/logout">Sair</a>' if logado else '<a class="nav-link login-btn" href="/login">Login</a>'
    
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html>
<head>
    <title>Consulta | JADLOG BRAS</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        .bg-jadlog {{ background: #E31E24; }}
        .btn-jadlog {{ background: #E31E24; color: white; border: none; padding: 10px 20px; border-radius: 8px; }}
        .btn-jadlog:hover {{ background: #B81217; color: white; }}
        .btn-jadlog-outline {{ background: transparent; color: #E31E24; border: 2px solid #E31E24; padding: 10px 20px; border-radius: 8px; }}
        .btn-jadlog-outline:hover {{ background: #E31E24; color: white; }}
        .btn-nova-cotacao {{ background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 8px; }}
        .btn-nova-cotacao:hover {{ background: #5a6268; color: white; }}
        .footer {{ background: #212529; color: white; padding: 15px 0; margin-top: 40px; text-align: center; }}
        .nav-link {{ color: white !important; }}
        .navbar-brand {{ color: white !important; font-weight: 700; display: flex; align-items: center; gap: 10px; text-decoration: none; }}
        .logo-img {{ height: 55px; background: white; padding: 5px 15px; border-radius: 60px; }}
        .nav-link.login-btn {{ background: white; color: #E31E24 !important; padding: 5px 20px; border-radius: 20px; font-weight: 600; }}
        .nav-link.login-btn:hover {{ background: #f0f0f0; }}
        .brand-text {{ color: white; font-size: 1.3rem; font-weight: 700; margin-left: 5px; }}
        .main-container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .search-box {{ background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); text-align: center; }}
        .search-box h2 {{ color: #E31E24; margin-bottom: 20px; }}
        .search-box .input-group {{ max-width: 500px; margin: 0 auto; }}
        .resultado-item {{ border-left: 4px solid #E31E24; margin-bottom: 12px; padding: 10px 15px; background: #f8f9fa; border-radius: 0 8px 8px 0; }}
        .resultado-item .label {{ font-weight: 600; color: #6c757d; font-size: 0.8rem; text-transform: uppercase; }}
        .resultado-item .valor {{ font-size: 1rem; font-weight: 500; color: #212529; }}
        .valor-frete {{ font-size: 1.3rem; font-weight: 700; color: #E31E24; }}
        .valor-total {{ font-size: 1.3rem; font-weight: 700; color: #28a745; }}
        .loading {{ text-align: center; padding: 30px; }}
        .loading .spinner-border {{ width: 3rem; height: 3rem; }}
        .search-icon {{ font-size: 2.5rem; color: #E31E24; margin-bottom: 15px; }}
        .botoes-acao {{ display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin-top: 20px; }}
        .botoes-acao .btn {{ min-width: 140px; }}
        .form-control:focus {{ border-color: #E31E24; box-shadow: 0 0 0 0.2rem rgba(227, 30, 36, 0.25); }}
        .cotacao-numero {{ font-size: 1rem; font-weight: 600; color: #E31E24; text-align: center; margin-bottom: 15px; }}
        .observacao {{ font-size: 0.8rem; color: #6c757d; text-align: center; margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 8px; border: 1px solid #ffeeba; }}
        .cliente-info {{ background: #f8f9fa; border-radius: 6px; padding: 10px 15px; margin: 10px 0; border: 1px solid #dee2e6; }}
        .cliente-info .nome {{ font-weight: 600; font-size: 0.95rem; }}
        .cliente-info .detalhes {{ color: #6c757d; font-size: 0.8rem; }}
        .card-shadow {{ background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); padding: 24px; margin-top: 20px; }}
        .row-resultado {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .col-resultado {{ flex: 1; min-width: 150px; }}
        @media (max-width: 768px) {{ .col-resultado {{ min-width: 100%; }} }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg bg-jadlog">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/img/logo-jadlog.png" alt="JADLOG BRAS" class="logo-img">
                <span class="brand-text">JADLOG BRAS</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMenu">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Inicio</a></li>
                    <li class="nav-item"><a class="nav-link" href="/simulador">Simulador</a></li>
                    <li class="nav-item"><a class="nav-link" href="/consulta">Consulta</a></li>
                    <li class="nav-item"><a class="nav-link" href="/rastreio">Rastreio</a></li>
                    <li class="nav-item">{botao_menu}</li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container-fluid main-container">
        <div class="search-box">
            <div class="search-icon"><i class="bi bi-file-text"></i></div>
            <h2>CONSULTA DE COTACOES</h2>
            <p class="text-muted">Digite o numero da cotacao para consultar.</p>
            
            <div class="input-group">
                <input type="text" class="form-control form-control-lg" 
                       placeholder="Ex: COT-2026-0806-1234" id="numeroCotacao">
                <button class="btn btn-jadlog" onclick="consultarCotacao()">
                    <i class="bi bi-search"></i> Consultar
                </button>
            </div>
            
            <div id="resultado" class="mt-4"></div>
            <div id="areaBotoes" style="display: none;"></div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">&copy; 2026 JADLOG BRAS</div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const USUARIO_LOGADO = {'true' if logado else 'false'};
        let dadosCotacao = null;
        
        function consultarCotacao() {
            const numero = document.getElementById('numeroCotacao').value.trim();
            const resultado = document.getElementById('resultado');
            
            if (!numero) {
                resultado.innerHTML = '<div class="alert alert-warning">Digite o numero da cotacao.</div>';
                return;
            }
            
            resultado.innerHTML = `
                <div class="loading">
                    <div class="spinner-border text-danger" role="status"></div>
                    <p class="mt-2">Consultando cotacao: ${numero}...</p>
                </div>
            `;
            document.getElementById('areaBotoes').style.display = 'none';
            
            // Simulação - substituir pela API real
            setTimeout(() => {
                resultado.innerHTML = '<div class="alert alert-info">Funcionalidade em desenvolvimento. Em breve voce podera consultar suas cotacoes salvas.</div>';
            }, 1500);
        }
    </script>
</body>
</html>
    """)