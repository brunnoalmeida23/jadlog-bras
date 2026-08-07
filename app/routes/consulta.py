# app/routes/consulta.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.sessao import sessoes
import json
import os
from datetime import datetime

router = APIRouter(prefix="/consulta", tags=["Consulta"])

# Arquivo para salvar as cotações
ARQUIVO_COTACOES = "cotacoes.json"

def carregar_cotacoes():
    """Carrega as cotações do arquivo JSON"""
    if os.path.exists(ARQUIVO_COTACOES):
        with open(ARQUIVO_COTACOES, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_cotacao(dados):
    """Salva uma cotação no arquivo JSON"""
    cotacoes = carregar_cotacoes()
    cotacoes.append(dados)
    with open(ARQUIVO_COTACOES, 'w', encoding='utf-8') as f:
        json.dump(cotacoes, f, ensure_ascii=False, indent=2)
    return dados

def buscar_cotacao_por_numero(numero):
    """Busca uma cotação pelo número"""
    cotacoes = carregar_cotacoes()
    for cotacao in cotacoes:
        if cotacao.get("numero") == numero:
            return cotacao
    return None

@router.get("/", response_class=HTMLResponse)
async def consulta_page(request: Request):
    token = request.cookies.get("auth_token")
    logado = token and token in sessoes
    
    botao_menu = '<a class="nav-link" href="/logout">Sair</a>' if logado else '<a class="nav-link login-btn" href="/login">Login</a>'
    
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html>
<head>
    <title>Consulta | JADLOG BRÁS</title>
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
        
        .main-container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        
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
        
        .resultado-item {{
            border-left: 4px solid #E31E24;
            margin-bottom: 12px;
            padding: 10px 15px;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
        }}
        
        .resultado-item .label {{
            font-weight: 600;
            color: #6c757d;
            font-size: 0.8rem;
            text-transform: uppercase;
        }}
        
        .resultado-item .valor {{
            font-size: 1rem;
            font-weight: 500;
            color: #212529;
        }}
        
        .valor-frete {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #E31E24;
        }}
        
        .valor-total {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #28a745;
        }}
        
        .loading {{
            text-align: center;
            padding: 30px;
        }}
        
        .loading .spinner-border {{
            width: 3rem;
            height: 3rem;
        }}
        
        .search-icon {{
            font-size: 2.5rem;
            color: #E31E24;
            margin-bottom: 15px;
        }}
        
        .botoes-acao {{
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        
        .botoes-acao .btn {{
            min-width: 140px;
        }}
        
        .form-control:focus {{
            border-color: #E31E24;
            box-shadow: 0 0 0 0.2rem rgba(227, 30, 36, 0.25);
        }}
        
        .cotacao-numero {{
            font-size: 1rem;
            font-weight: 600;
            color: #E31E24;
            text-align: center;
            margin-bottom: 15px;
        }}
        
        .observacao {{
            font-size: 0.8rem;
            color: #6c757d;
            text-align: center;
            margin-top: 15px;
            padding: 10px;
            background: #fff3cd;
            border-radius: 8px;
            border: 1px solid #ffeeba;
        }}
        
        .cliente-info {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 10px 15px;
            margin: 10px 0;
            border: 1px solid #dee2e6;
        }}
        
        .cliente-info .nome {{
            font-weight: 600;
            font-size: 0.95rem;
        }}
        
        .cliente-info .detalhes {{
            color: #6c757d;
            font-size: 0.8rem;
        }}
        
        .card-shadow {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            padding: 24px;
            margin-top: 20px;
        }}
        
        .row-resultado {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .col-resultado {{
            flex: 1;
            min-width: 150px;
        }}
        
        @media (max-width: 768px) {{
            .col-resultado {{
                min-width: 100%;
            }}
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
        <div class="container">&copy; 2026 JADLOG BRÁS</div>
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
            
            fetch(`/consulta/buscar?numero=${encodeURIComponent(numero)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.encontrado) {
                        const cotacao = data.cotacao;
                        dadosCotacao = cotacao;
                        exibirResultado(cotacao);
                        document.getElementById('areaBotoes').style.display = 'block';
                        document.getElementById('areaBotoes').innerHTML = gerarBotoes();
                    } else {
                        resultado.innerHTML = `<div class="alert alert-danger">Cotacao ${numero} nao encontrada.</div>`;
                    }
                })
                .catch(() => {
                    resultado.innerHTML = '<div class="alert alert-warning">Erro ao consultar cotacao. Tente novamente.</div>';
                });
        }
        
        function exibirResultado(data) {
            const resultado = document.getElementById('resultado');
            
            let html = `
                <div class="card-shadow text-start">
                    <div class="cotacao-numero"><i class="bi bi-file-text"></i> ${data.numero}</div>
                    <div class="cliente-info">
                        <div class="nome">${data.nome_cliente || 'Cliente nao informado'}</div>
                        <div class="detalhes">CPF: ${data.cpf_cliente || 'N/A'} • ${data.cidade_destino || ''}/${data.uf_destino || ''}</div>
                    </div>
                    <div class="row-resultado">
                        <div class="col-resultado">
                            <div class="resultado-item"><div class="label">Origem</div><div class="valor">${data.origem || 'Bras - SP'}</div></div>
                            <div class="resultado-item"><div class="label">Destino</div><div class="valor">${data.cidade_destino || 'N/A'}/${data.uf_destino || 'N/A'}</div></div>
                            <div class="resultado-item"><div class="label">Prazo</div><div class="valor">${data.prazo || 'N/A'} dias</div></div>
                        </div>
                        <div class="col-resultado">
                            <div class="resultado-item"><div class="label">Tipo</div><div class="valor">${data.tipo_tarifa || 'N/A'}</div></div>
                            <div class="resultado-item"><div class="label">Peso</div><div class="valor">${data.peso || 'N/A'} kg</div></div>
                            <div class="resultado-item"><div class="label">Modalidade</div><div class="valor">${data.modalidade || 'N/A'}</div></div>
                        </div>
                    </div>
                    <hr>
                    <div class="row g-2">
                        <div class="col-md-4"><div class="resultado-item"><div class="label">Valor do Frete</div><div class="valor valor-frete">R$ ${(data.valor_frete || 0).toFixed(2)}</div></div></div>
                        <div class="col-md-4"><div class="resultado-item"><div class="label">Seguro</div><div class="valor">R$ ${(data.seguro || 0).toFixed(2)}</div></div></div>
                        <div class="col-md-4"><div class="resultado-item" style="border-left-color: #28a745;"><div class="label">Frete Total</div><div class="valor valor-total">R$ ${(data.valor_total || 0).toFixed(2)}</div></div></div>
                    </div>
                    <div class="observacao"><i class="bi bi-info-circle"></i> VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRAS)<br><strong>Validos ate Dezembro de 2026</strong></div>
                </div>
            `;
            
            resultado.innerHTML = html;
        }
        
        function gerarBotoes() {
            const logado = USUARIO_LOGADO;
            let botoes = '<div class="botoes-acao">';
            if (logado) {
                botoes += `<button class="btn btn-jadlog" onclick="imprimirCotacao()"><i class="bi bi-printer"></i> Imprimir</button>`;
            }
            botoes += `
                <button class="btn btn-jadlog-outline" onclick="baixarCotacao()"><i class="bi bi-download"></i> Baixar</button>
                <button class="btn btn-nova-cotacao" onclick="novaConsulta()"><i class="bi bi-plus-circle"></i> Nova Consulta</button>
            </div>`;
            return botoes;
        }
        
        function novaConsulta() {
            document.getElementById('numeroCotacao').value = '';
            document.getElementById('resultado').innerHTML = '';
            document.getElementById('areaBotoes').style.display = 'none';
            dadosCotacao = null;
            document.getElementById('numeroCotacao').focus();
        }
        
        function imprimirCotacao() {
            if (!dadosCotacao) { alert('Nenhuma cotacao para imprimir.'); return; }
            const janela = window.open('', '_blank', 'width=800,height=600');
            janela.document.write(gerarHTML(dadosCotacao));
            janela.document.close();
            janela.focus();
            janela.print();
            janela.close();
        }
        
        function baixarCotacao() {
            if (!dadosCotacao) { alert('Nenhuma cotacao para baixar.'); return; }
            const blob = new Blob([gerarHTML(dadosCotacao)], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Cotacao_${dadosCotacao.numero || 'consulta'}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        function gerarHTML(data) {
            return `<!DOCTYPE html>
            <html>
            <head><title>Cotacao - JADLOG BRAS</title>
            <meta charset="UTF-8">
            <style>
                body{font-family:Arial;padding:30px;max-width:600px;margin:0 auto}
                .header{text-align:center;border-bottom:2px solid #E31E24;padding-bottom:10px}
                .header h1{color:#E31E24;margin:0;font-size:1.5rem}
                .header h2{font-size:1.1rem;color:#555;margin:5px 0}
                .numero{text-align:center;font-weight:bold;color:#E31E24;margin:15px 0;font-size:1rem}
                .linha{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #eee}
                .label{font-weight:bold;color:#555}
                .valor{font-weight:500}
                .total{font-size:1.3rem;font-weight:bold;color:#28a745;text-align:center;padding:15px;background:#f0f8f0;border-radius:8px;margin:15px 0}
                .obs{text-align:center;padding:10px;background:#fff3cd;border-radius:8px;border:1px solid #ffeeba;font-size:0.8rem;margin:15px 0}
                .footer{text-align:center;margin-top:30px;font-size:11px;color:#999;border-top:1px solid #ddd;padding-top:10px}
            </style>
            </head>
            <body>
                <div class="header"><h1>JADLOG BRAS</h1><h2>Cotacao de Frete</h2></div>
                <div class="numero">${data.numero}</div>
                <div class="linha"><span class="label">Cliente</span><span class="valor">${data.nome_cliente || 'N/A'}</span></div>
                <div class="linha"><span class="label">CPF</span><span class="valor">${data.cpf_cliente || 'N/A'}</span></div>
                <div class="linha"><span class="label">Origem</span><span class="valor">${data.origem || 'Bras - SP'}</span></div>
                <div class="linha"><span class="label">Destino</span><span class="valor">${data.cidade_destino || 'N/A'}/${data.uf_destino || 'N/A'}</span></div>
                <div class="linha"><span class="label">Prazo</span><span class="valor">${data.prazo || 'N/A'} dias</span></div>
                <div class="linha"><span class="label">Tipo</span><span class="valor">${data.tipo_tarifa || 'N/A'}</span></div>
                <div class="linha"><span class="label">Peso</span><span class="valor">${data.peso || 'N/A'} kg</span></div>
                <div class="linha"><span class="label">Modalidade</span><span class="valor">${data.modalidade || 'N/A'}</span></div>
                <div class="linha"><span class="label">Valor do Frete</span><span class="valor">R$ ${(data.valor_frete || 0).toFixed(2)}</span></div>
                <div class="linha"><span class="label">Seguro</span><span class="valor">R$ ${(data.seguro || 0).toFixed(2)}</span></div>
                <div class="total">Frete Total: R$ ${(data.valor_total || 0).toFixed(2)}</div>
                <div class="obs">VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRAS)<br><strong>Validos ate Dezembro de 2026</strong></div>
                <div class="footer"><p>JADLOG BRAS - Sistema de Cotacao de Frete</p></div>
            </body>
            </html>`;
        }
    </script>
</body>
</html>
    """)