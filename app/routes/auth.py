# app/routes/auth.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import secrets
from app.services.sessao import sessoes

router = APIRouter(prefix="", tags=["Autenticação"])

SENHA_CORRETA = os.getenv("FUNCIONARIO_SENHA", "JadLog2026")


@router.get("/login", response_class=HTMLResponse)
async def pagina_login(request: Request):
    token = request.cookies.get("auth_token")
    if token and token in sessoes:
        return RedirectResponse(url="/simulador", status_code=303)
    
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Login | JADLOG BRÁS</title>
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
        <div class="row justify-content-center py-5">
            <div class="col-md-6 col-lg-4">
                <div class="card border-0 shadow rounded-4">
                    <div class="card-body p-4 p-md-5">
                        <div class="text-center mb-4">
                            <img src="/static/img/logo-jadlog.png" alt="Jadlog Brás" style="max-width: 170px;" class="mb-4">
                            <h3 class="fw-bold mb-1">Acesso do funcionário</h3>
                            <p class="text-muted mb-0">Digite a senha da unidade.</p>
                        </div>
                        
                        <div id="erroLogin" class="alert alert-danger d-none"></div>
                        
                        <form id="formLogin" method="POST" action="/login">
                            <div class="mb-4">
                                <label for="senha" class="form-label fw-bold">Senha</label>
                                <input type="password" class="form-control form-control-lg" id="senha" name="senha" autocomplete="off" autofocus required>
                            </div>
                            <button type="submit" class="btn btn-danger btn-lg w-100">
                                <i class="bi bi-box-arrow-in-right me-2"></i> Entrar
                            </button>
                        </form>
                        
                        <p class="text-center text-muted small mt-4 mb-0">A sessão permanece ativa por 8 horas.</p>
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
        document.getElementById('formLogin').addEventListener('submit', function(e) {
            e.preventDefault();
            const senha = document.getElementById('senha').value;
            const erroDiv = document.getElementById('erroLogin');
            
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `senha=${encodeURIComponent(senha)}`
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json().then(data => {
                        erroDiv.textContent = data.erro || 'Senha incorreta.';
                        erroDiv.classList.remove('d-none');
                    });
                }
            })
            .catch(() => {
                erroDiv.textContent = 'Erro ao tentar fazer login. Tente novamente.';
                erroDiv.classList.remove('d-none');
            });
        });
    </script>
</body>
</html>
    """


@router.post("/login")
async def realizar_login(request: Request, senha: str = Form(...)):
    if senha != SENHA_CORRETA:
        return {"erro": "Senha incorreta."}
    
    token = secrets.token_urlsafe(32)
    sessoes[token] = True
    
    response = RedirectResponse(url="/simulador", status_code=303)
    response.set_cookie(key="auth_token", value=token, max_age=28800, httponly=True)
    return response


@router.get("/logout")
async def logout(request: Request):
    token = request.cookies.get("auth_token")
    if token in sessoes:
        del sessoes[token]
    
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("auth_token")
    return response