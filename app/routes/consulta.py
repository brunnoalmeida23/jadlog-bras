from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.services.sessao import sessoes

router = APIRouter(prefix="/consulta", tags=["Consulta"])


@router.get("/", response_class=HTMLResponse)
async def consulta_page(request: Request):
    token = request.cookies.get("auth_token")
    logado = bool(token and token in sessoes)
    botao_menu = '<a class="nav-link" href="/logout">Sair</a>' if logado else '<a class="nav-link login-btn" href="/login">Login</a>'
    
    html = r'''<!DOCTYPE html>
<html><head>
    <title>Consulta | JADLOG BRÁS</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <link rel="manifest" href="/static/manifest.json">
    <link rel="apple-touch-icon" href="/static/icons/launchericon-192x192.png">
    <meta name="theme-color" content="#E31E24">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>body{background:#f6f7f9}.bg-jadlog{background:#E31E24}.nav-link{color:white!important}.navbar-brand{color:white!important;font-weight:700;display:flex;align-items:center;gap:10px}.logo-img{height:55px;background:white;padding:5px 15px;border-radius:60px}.login-btn{background:white;color:#E31E24!important;padding:5px 20px!important;border-radius:20px}.search-box{max-width:850px;margin:35px auto;background:white;padding:28px;border-radius:14px;box-shadow:0 2px 12px #00000015}.btn-jadlog{background:#E31E24;color:white}.resultado-item{padding:8px 0;border-bottom:1px solid #eee}.label{font-size:.78rem;color:#6c757d;text-transform:uppercase}.valor{font-weight:600}.valor-total{font-size:1.25rem;color:#198754}.footer{background:#212529;color:white;padding:15px;text-align:center;margin-top:40px}</style></head>
<body><nav class="navbar navbar-expand-lg bg-jadlog"><div class="container"><a class="navbar-brand" href="/"><img src="/static/img/logo-jadlog.png" class="logo-img"></a><div class="navbar-nav ms-auto"><a class="nav-link" href="/">Início</a><a class="nav-link" href="/simulador">Simulador</a><a class="nav-link" href="/consulta">Consulta</a><a class="nav-link" href="/rastreio">Rastreio</a>__BOTAO__</div></div></nav>
<main class="container"><div class="search-box"><h3 class="mb-1" style="color:#E31E24"><i class="bi bi-search"></i> CONSULTA DE COTAÇÕES</h3><p class="text-muted">Digite o número da cotação.</p><div class="input-group"><input id="numeroCotacao" class="form-control form-control-lg" placeholder="Ex: COT-2026-0807-1234"><button class="btn btn-jadlog" onclick="consultarCotacao()">Consultar</button></div><div id="resultado" class="mt-4"></div></div></main><footer class="footer">&copy; 2026 JADLOG BRÁS</footer>
<script>
async function consultarCotacao(){const n=document.getElementById('numeroCotacao').value.trim(),r=document.getElementById('resultado');if(!n){r.innerHTML='<div class="alert alert-warning">Digite o número da cotação.</div>';return;}r.innerHTML='<div class="text-center p-4"><div class="spinner-border text-danger"></div></div>';try{const resp=await fetch('/api/cotacao/buscar?numero='+encodeURIComponent(n));const data=await resp.json();if(!resp.ok){throw new Error(data.erro||'Erro na consulta');}if(!data.encontrado){r.innerHTML='<div class="alert alert-danger">Cotação não encontrada.</div>';return;}const c=data.cotacao||{};const money=v=>'R$ '+Number(v||0).toFixed(2).replace('.',',');r.innerHTML=`<div class="card border-0"><div class="card-body"><h5 class="text-danger">${c.numero||n}</h5><div class="resultado-item"><div class="label">Cliente</div><div class="valor">${c.nome_cliente||'Não informado'}</div></div><div class="resultado-item"><div class="label">Destino</div><div class="valor">${c.cidade_destino||c.cidade||''}/${c.uf_destino||c.uf||''}</div></div><div class="resultado-item"><div class="label">Modalidade</div><div class="valor">${c.modalidade||''}</div></div><div class="resultado-item"><div class="label">Peso</div><div class="valor">${c.peso||''} kg</div></div><div class="resultado-item"><div class="label">Frete total</div><div class="valor valor-total">${money(c.valor_total||c.total||c.preco_final||c.frete)}</div></div></div></div>`;}catch(e){r.innerHTML='<div class="alert alert-danger">'+e.message+'</div>';}}
</script>
<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(function(reg) {
                console.log('Service Worker registrado com sucesso!');
            })
            .catch(function(err) {
                console.log('Erro ao registrar Service Worker:', err);
            });
    }
</script>
</body></html>'''
    
    html_final = html.replace("__BOTAO__", botao_menu)
    return HTMLResponse(html_final)