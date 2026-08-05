# app/routes/home.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="", tags=["Home"])

@router.get("/", response_class=HTMLResponse)
async def home_page():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>JADLOG BRÁS</title>
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
        .navbar-brand { color: white !important; font-weight: 700; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg bg-jadlog">
        <div class="container">
            <a class="navbar-brand" href="/">JADLOG BRÁS</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMenu">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="/">Início</a></li>
                    <li class="nav-item"><a class="nav-link" href="/simulador">Simulador</a></li>
                    <li class="nav-item"><a class="nav-link" href="/consulta">Consulta</a></li>
                    <li class="nav-item"><a class="nav-link" href="/rastreio">Rastreio</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container py-4">
        <div class="row">
            <div class="col-lg-8 mx-auto text-center">
                <h1 class="display-4 fw-bold text-danger">
                    <i class="bi bi-truck me-3"></i>JADLOG BRÁS
                </h1>
                <p class="lead">Sistema de Cotação de Frete</p>
                <p class="text-muted">
                    Bem-vindo ao sistema de cotações da unidade da Av. Vautier, 455 - Brás, São Paulo.
                </p>
                <div class="d-flex gap-3 justify-content-center mt-4 flex-wrap">
                    <a href="/simulador" class="btn btn-jadlog btn-lg">
                        <i class="bi bi-calculator me-2"></i>Simular Frete
                    </a>
                    <a href="/consulta" class="btn btn-outline-secondary btn-lg">
                        <i class="bi bi-search me-2"></i>Consultar
                    </a>
                    <a href="/rastreio" class="btn btn-outline-secondary btn-lg">
                        <i class="bi bi-truck me-2"></i>Rastrear
                    </a>
                </div>
            </div>
        </div>

        <div class="row mt-5">
            <div class="col-md-4">
                <div class="card-shadow text-center">
                    <i class="bi bi-calculator display-4 text-danger mb-3"></i>
                    <h5>Simulação de Frete</h5>
                    <p class="text-muted">Calcule o valor do frete com base no peso, destino e modalidade.</p>
                    <a href="/simulador" class="btn btn-jadlog">Simular Agora</a>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card-shadow text-center">
                    <i class="bi bi-search display-4 text-danger mb-3"></i>
                    <h5>Consulta de Cotações</h5>
                    <p class="text-muted">Consulte cotações já realizadas por número de cotação.</p>
                    <a href="/consulta" class="btn btn-jadlog">Consultar</a>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card-shadow text-center">
                    <i class="bi bi-truck display-4 text-danger mb-3"></i>
                    <h5>Rastreio</h5>
                    <p class="text-muted">Acompanhe o status da sua encomenda pelo código de rastreio.</p>
                    <a href="/rastreio" class="btn btn-jadlog">Rastrear</a>
                </div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">&copy; 2026 JADLOG BRÁS</div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """

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