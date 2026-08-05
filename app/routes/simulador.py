# app/routes/simulador.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.services.sessao import sessoes

router = APIRouter(prefix="/simulador", tags=["Simulador"])


@router.get("/", response_class=HTMLResponse)
async def simulador_page(request: Request):
    token = request.cookies.get("auth_token")
    logado = token and token in sessoes
    botao_menu = '<a class="nav-link" href="/logout">Sair</a>' if logado else '<a class="nav-link login-btn" href="/login">Login</a>'
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Simulador | JADLOG BRÁS</title>
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
        .result-box {{ background: #f8f9fa; border-radius: 8px; padding: 20px; margin-top: 20px; }}
        .cotacao-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e9ecef; }}
        .cotacao-item:last-child {{ border-bottom: none; }}
        .total {{ font-weight: bold; font-size: 1.2rem; color: #E31E24; }}
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
        <div class="row">
            <div class="col-lg-6">
                <h2 class="mb-4" style="color: #E31E24;">Simular Frete</h2>
                <div class="card card-shadow">
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label fw-bold">CEP de Destino</label>
                            <input type="text" class="form-control" id="cep" placeholder="Ex: 01000-000 (SP Capital) ou 69945-000 (Interior)">
                            <small class="text-muted">Ex: 01000-000 (SP Capital) ou 69945-000 (Interior)</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Peso (kg)</label>
                            <input type="number" class="form-control" id="peso" placeholder="Ex: 2.350" step="0.001">
                            <small class="text-muted">Ex: 2.350</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Valor da NF (R$)</label>
                            <input type="number" class="form-control" id="valorNf" placeholder="Ex: 5000.00" step="0.01">
                            <small class="text-muted">Ex: 5000.00</small>
                            <small class="text-muted d-block">Seguro: 0,66% do valor da NF (se NF > R$ 100)</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Modalidade</label>
                            <div class="d-flex gap-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="modalidade" id="package" value="PACKAGE" checked>
                                    <label class="form-check-label" for="package">PACKAGE</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="modalidade" id="com" value=".COM">
                                    <label class="form-check-label" for="com">.COM</label>
                                </div>
                            </div>
                            <small class="text-muted">Selecione a modalidade desejada para o frete</small>
                        </div>
                        <button class="btn btn-jadlog w-100" onclick="calcularFrete()">
                            <i class="bi bi-calculator me-2"></i>Calcular Frete
                        </button>
                    </div>
                </div>
            </div>

            <div class="col-lg-6">
                <h2 class="mb-4" style="color: #E31E24;">Resultado da Cotação</h2>
                <div class="card card-shadow">
                    <div class="card-body" id="resultado">
                        <p class="text-muted text-center mb-0">Preencha os dados ao lado<br>e clique em Calcular Frete</p>
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
        function calcularFrete() {{
            const cep = document.getElementById('cep').value;
            const peso = document.getElementById('peso').value;
            const valorNf = document.getElementById('valorNf').value;
            const modalidade = document.querySelector('input[name="modalidade"]:checked').value;
            const resultado = document.getElementById('resultado');
            
            if (!cep || !peso) {{
                resultado.innerHTML = '<div class="alert alert-warning">Preencha CEP e Peso.</div>';
                return;
            }}
            
            resultado.innerHTML = '<div class="text-center"><div class="spinner-border text-danger" role="status"></div><p>Calculando...</p></div>';
            
            fetch(`/api/calcular-frete?cep=${{cep}}&peso=${{peso}}&modalidade=${{modalidade}}&valor_nf=${{valorNf || 0}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        const d = data.dados;
                        resultado.innerHTML = `
                            <div class="result-box">
                                <div class="cotacao-item"><span>CEP</span><span><strong>${{d.cep}}</strong></span></div>
                                <div class="cotacao-item"><span>Destino</span><span><strong>${{d.cidade}}/${{d.uf}}</strong></span></div>
                                <div class="cotacao-item"><span>Tipo</span><span><strong>${{d.tipo_tarifa}}</strong></span></div>
                                <div class="cotacao-item"><span>Prazo</span><span><strong>${{d.prazo}} dias úteis</strong></span></div>
                                <div class="cotacao-item"><span>Peso</span><span><strong>${{d.peso}} kg</strong></span></div>
                                <div class="cotacao-item"><span>Modalidade</span><span><strong>${{d.modalidade}}</strong></span></div>
                                <div class="cotacao-item"><span>GLM</span><span><strong>R$ ${{d.glm}}</strong></span></div>
                                <div class="cotacao-item"><span>Lucro</span><span><strong>R$ ${{d.lucro}}</strong></span></div>
                                <div class="cotacao-item"><span>Valor do Frete</span><span><strong>R$ ${{d.preco_final}}</strong></span></div>
                                <div class="cotacao-item"><span>Seguro</span><span><strong>R$ ${{d.ad_valorem}}</strong></span></div>
                                <div class="cotacao-item total"><span>Frete Total</span><span><strong>R$ ${{d.total}}</strong></span></div>
                            </div>
                        `;
                    }} else {{
                        resultado.innerHTML = `<div class="alert alert-danger">${{data.erro || 'Erro ao calcular frete'}}</div>`;
                    }}
                }})
                .catch(() => {{
                    resultado.innerHTML = '<div class="alert alert-danger">Erro ao conectar com o servidor.</div>';
                }});
        }}
    </script>
</body>
</html>
    """