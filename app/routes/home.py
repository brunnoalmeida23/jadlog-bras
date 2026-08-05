# app/routes/home.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="", tags=["Home"])

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
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
        .navbar-brand { color: white !important; font-weight: 700; display: flex; align-items: center; gap: 10px; text-decoration: none; }
        .logo-img { 
            height: 45px; 
            background: white; 
            padding: 5px 15px; 
            border-radius: 6px; 
        }
        .nav-link.login-btn { 
            background: white; 
            color: #E31E24 !important; 
            padding: 5px 20px; 
            border-radius: 20px; 
            font-weight: 600;
        }
        .nav-link.login-btn:hover { background: #f0f0f0; }
        .brand-text { 
            color: white; 
            font-size: 1.3rem; 
            font-weight: 700; 
            margin-left: 5px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg bg-jadlog">
        <div class="container">
            <a class="navbar-brand" href="/">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <img src="/static/img/logo-jadlog.png" alt="JADLOG BRÁS" class="logo-img">
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
                <div class="text-center mb-5">
                    <h1 class="display-5 fw-bold" style="color: #E31E24;">
                        Bem-vindo ao sistema de cotação de fretes
                    </h1>
                </div>
                <div class="row g-4">
                    <div class="col-md-4">
                        <div class="card card-shadow h-100 text-center">
                            <div class="card-body d-flex flex-column">
                                <div class="mb-3" style="font-size: 3rem; color: #E31E24;">
                                    <i class="bi bi-calculator"></i>
                                </div>
                                <h5 class="card-title fw-bold">Simulação de Frete</h5>
                                <p class="card-text text-muted">Calcule o valor do frete com base no peso, destino e modalidade.</p>
                                <a href="/simulador" class="btn btn-jadlog mt-auto">Simular Agora</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card card-shadow h-100 text-center">
                            <div class="card-body d-flex flex-column">
                                <div class="mb-3" style="font-size: 3rem; color: #E31E24;">
                                    <i class="bi bi-search"></i>
                                </div>
                                <h5 class="card-title fw-bold">Consulta de Cotações</h5>
                                <p class="card-text text-muted">Consulte cotações já realizadas por número de cotação.</p>
                                <a href="/consulta" class="btn btn-jadlog mt-auto">Consultar</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card card-shadow h-100 text-center">
                            <div class="card-body d-flex flex-column">
                                <div class="mb-3" style="font-size: 3rem; color: #E31E24;">
                                    <i class="bi bi-truck"></i>
                                </div>
                                <h5 class="card-title fw-bold">Rastreio</h5>
                                <p class="card-text text-muted">Acompanhe o status da sua encomenda pelo código de rastreio.</p>
                                <a href="/rastreio" class="btn btn-jadlog mt-auto">Rastrear</a>
                            </div>
                        </div>
                    </div>
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