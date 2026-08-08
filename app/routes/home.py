# app/routes/home.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.services.sessao import sessoes

router = APIRouter(prefix="", tags=["Home"])


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    token = request.cookies.get("auth_token")
    logado = token and token in sessoes
    botao_menu = '<a class="nav-link" href="/logout">Sair</a>' if logado else '<a class="nav-link login-btn" href="/login">Login</a>'
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>JADLOG BRÁS</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="manifest" href="/static/manifest.json">
    <link rel="apple-touch-icon" href="/static/icons/launchericon-192x192.png">
    <meta name="theme-color" content="#E31E24">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
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
        .install-app-area {{ display: none; margin-top: 24px; }}
        .btn-install-app {{ display: inline-flex; align-items: center; justify-content: center; gap: 8px; background: #212529; color: white; border: none; padding: 12px 24px; border-radius: 10px; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.16); }}
        .btn-install-app:hover {{ background: #000; color: white; }}


        /* SPLASH ANIMADA DO PWA */
        #appSplash {{
            position: fixed;
            inset: 0;
            z-index: 99999;
            display: none;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background: #E31E24;
            color: #fff;
            opacity: 1;
            transition: opacity .42s ease, visibility .42s ease;
        }}
        #appSplash.splash-visible {{ display: flex; }}
        #appSplash.splash-hide {{ opacity: 0; visibility: hidden; pointer-events: none; }}
        .splash-content {{
            width: min(88vw, 420px);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            transform: translateY(-1vh);
        }}
        .splash-logo-stage {{
            position: relative;
            width: 230px;
            height: 230px;
            display: grid;
            place-items: center;
            margin-bottom: 28px;
        }}
        .splash-ring {{
            position: absolute;
            left: 50%; top: 50%;
            width: 122px; height: 122px;
            border: 2px solid rgba(255,255,255,.62);
            border-radius: 50%;
            transform: translate(-50%, -50%) scale(.72);
            opacity: 0;
            animation: ondaJadlog 2.25s cubic-bezier(.2,.65,.35,1) infinite;
        }}
        .splash-ring.ring-2 {{ animation-delay: .72s; }}
        .splash-ring.ring-3 {{ animation-delay: 1.44s; }}
        @keyframes ondaJadlog {{
            0% {{ transform: translate(-50%, -50%) scale(.72); opacity: 0; }}
            14% {{ opacity: .62; }}
            72% {{ opacity: .18; }}
            100% {{ transform: translate(-50%, -50%) scale(1.78); opacity: 0; }}
        }}
        .splash-logo-card {{
            position: relative;
            z-index: 3;
            width: 130px; height: 130px;
            border-radius: 31px;
            overflow: hidden;
            background: #fff;
            display: grid;
            place-items: center;
            box-shadow: 0 12px 35px rgba(0,0,0,.20);
            animation: logoRespira 1.9s ease-in-out infinite;
        }}
        .splash-logo-card img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
        @keyframes logoRespira {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.035); }}
        }}
        .splash-title {{
            margin: 0;
            font-size: clamp(2rem, 8vw, 2.75rem);
            line-height: 1;
            font-weight: 800;
            letter-spacing: .02em;
            color: #fff;
        }}
        .splash-subtitle {{
            margin-top: 12px;
            font-size: clamp(.78rem, 3.2vw, 1rem);
            font-weight: 500;
            letter-spacing: .30em;
            padding-left: .30em;
            color: rgba(255,255,255,.96);
        }}
        .splash-loader {{ width: min(72vw, 310px); margin-top: 62px; }}
        .splash-loader-track {{
            position: relative;
            height: 5px;
            overflow: hidden;
            border-radius: 999px;
            background: rgba(255,255,255,.23);
        }}
        .splash-loader-progress {{
            position: absolute;
            inset: 0 auto 0 0;
            width: 42%;
            border-radius: inherit;
            background: #fff;
            box-shadow: 0 0 12px rgba(255,255,255,.88);
            animation: carregandoJadlog 1.35s ease-in-out infinite;
        }}
        @keyframes carregandoJadlog {{
            0% {{ width: 10%; transform: translateX(-100%); opacity: .65; }}
            45% {{ width: 48%; opacity: 1; }}
            100% {{ width: 28%; transform: translateX(330%); opacity: .75; }}
        }}
        .splash-loading-text {{
            margin-top: 18px;
            font-size: .88rem;
            letter-spacing: .10em;
            color: rgba(255,255,255,.94);
        }}

    </style>
</head>
<body>

    <div id="appSplash" aria-hidden="true">
        <div class="splash-content">
            <div class="splash-logo-stage">
                <span class="splash-ring ring-1"></span>
                <span class="splash-ring ring-2"></span>
                <span class="splash-ring ring-3"></span>
                <div class="splash-logo-card">
                    <img src="/static/icons/launchericon-512x512.png" alt="JADLOG BRÁS">
                </div>
            </div>
            <h1 class="splash-title">JADLOG BRÁS</h1>
            <div class="splash-subtitle">SIMULADOR DE FRETES</div>
            <div class="splash-loader">
                <div class="splash-loader-track"><div class="splash-loader-progress"></div></div>
                <div class="splash-loading-text">CARREGANDO...</div>
            </div>
        </div>
    </div>

    <nav class="navbar navbar-expand-lg bg-jadlog">
        <div class="container">
            <a class="navbar-brand" href="/">
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

                <div id="installAppArea" class="install-app-area text-center">
                    <button id="installAppButton" type="button" class="btn-install-app">
                        <i class="bi bi-phone"></i> Instalar aplicativo
                    </button>
                    <div class="text-muted small mt-2">Instale o JADLOG BRÁS como aplicativo no dispositivo.</div>
                </div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">&copy; 2026 JADLOG BRÁS</div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let deferredInstallPrompt = null;

        function estaEmModoApp() {{
            return window.matchMedia('(display-mode: standalone)').matches ||
                   window.navigator.standalone === true;
        }}

        function ocultarBotaoInstalacao() {{
            const area = document.getElementById('installAppArea');
            if (area) area.style.display = 'none';
        }}



        function iniciarSplashPWA() {{
            if (!estaEmModoApp()) {{
                return;
            }}

            if (sessionStorage.getItem('jadlogSplashShown') === '1') {{
                return;
            }}

            const splash = document.getElementById('appSplash');
            if (!splash) {{
                return;
            }}

            sessionStorage.setItem('jadlogSplashShown', '1');
            splash.classList.add('splash-visible');
            splash.setAttribute('aria-hidden', 'false');

            window.setTimeout(function() {{
                splash.classList.add('splash-hide');
                window.setTimeout(function() {{
                    splash.classList.remove('splash-visible');
                    splash.setAttribute('aria-hidden', 'true');
                }}, 450);
            }}, 1850);
        }}

        iniciarSplashPWA();

        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', function() {{
                navigator.serviceWorker.register('/sw.js')
                    .then(function(reg) {{
                        console.log('Service Worker registrado com sucesso!', reg.scope);
                    }})
                    .catch(function(err) {{
                        console.log('Erro ao registrar Service Worker:', err);
                    }});
            }});
        }}

        window.addEventListener('beforeinstallprompt', function(event) {{
            event.preventDefault();
            deferredInstallPrompt = event;

            if (!estaEmModoApp()) {{
                const area = document.getElementById('installAppArea');
                if (area) area.style.display = 'block';
            }}
        }});

        document.getElementById('installAppButton').addEventListener('click', async function() {{
            if (!deferredInstallPrompt) {{
                return;
            }}

            deferredInstallPrompt.prompt();
            const resultado = await deferredInstallPrompt.userChoice;
            console.log('Resultado da instalação:', resultado.outcome);

            deferredInstallPrompt = null;
            ocultarBotaoInstalacao();
        }});

        window.addEventListener('appinstalled', function() {{
            deferredInstallPrompt = null;
            ocultarBotaoInstalacao();
            console.log('JADLOG BRÁS instalado como PWA.');
        }});

        if (estaEmModoApp()) {{
            ocultarBotaoInstalacao();
        }}
    </script>
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