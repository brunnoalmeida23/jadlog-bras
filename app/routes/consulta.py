# app/routes/consulta.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/consulta", tags=["Consulta"])

@router.get("/", response_class=HTMLResponse)
async def consulta_page(request: Request):
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Consulta de Cotações | JADLOG BRÁS</title>
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
            <div class="col-lg-8">
                <h2 class="text-center mb-4" style="color: #E31E24;">Consulta de Cotações</h2>
                <div class="card card-shadow">
                    <div class="card-body">
                        <p class="text-muted text-center">
                            <i class="bi bi-search display-4 d-block mb-3" style="color: #E31E24;"></i>
                            Digite o número da cotação para consultar.
                        </p>
                        <div class="mt-4">
                            <div class="input-group">
                                <input type="text" class="form-control" placeholder="Ex: COT-2026-0001" id="codigoCotacao">
                                <button class="btn btn-jadlog" onclick="consultar()">Consultar</button>
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

    <script>
        function consultar() {
            const codigo = document.getElementById('codigoCotacao').value;
            const resultado = document.getElementById('resultado');
            
            if (!codigo) {
                resultado.innerHTML = '<div class="alert alert-warning">Digite um número de cotação.</div>';
                return;
            }
            
            // Faz a requisição para a API
            fetch(`/consulta/${codigo}`)
                .then(response => response.json())
                .then(data => {
                    if (data.mensagem) {
                        resultado.innerHTML = `<div class="alert alert-info">${data.mensagem}</div>`;
                    } else {
                        resultado.innerHTML = `<div class="alert alert-danger">Cotação não encontrada.</div>`;
                    }
                })
                .catch(() => {
                    resultado.innerHTML = `<div class="alert alert-danger">Erro ao consultar. Tente novamente.</div>`;
                });
        }
    </script>
</body>
</html>
    """

@router.get("/{codigo}")
async def consultar_cotacao(codigo: str):
    # Aqui você pode implementar a lógica de consulta
    return {"mensagem": f"Consultando cotação: {codigo}"}