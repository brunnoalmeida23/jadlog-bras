# app/routes/simulador.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.services.sessao import sessoes
import datetime

router = APIRouter(prefix="/simulador", tags=["Simulador"])

@router.get("/", response_class=HTMLResponse)
async def simulador_page(request: Request):
    token = request.cookies.get("auth_token")
    logado = token and token in sessoes
    
    now = datetime.datetime.now()
    num_cotacao = f"COT-{now.year}-{str(now.month).zfill(2)}{str(now.day).zfill(2)}-{str(now.hour).zfill(2)}{str(now.minute).zfill(2)}"
    
    botao_menu = '<a class="nav-link" href="/logout">Sair</a>' if logado else '<a class="nav-link login-btn" href="/login">Login</a>'
    
    return HTMLResponse(content=f"""
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
        .btn-jadlog-outline {{ background: transparent; color: #E31E24; border: 2px solid #E31E24; padding: 10px 30px; border-radius: 8px; }}
        .btn-jadlog-outline:hover {{ background: #E31E24; color: white; }}
        .card-shadow {{ background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); padding: 24px; }}
        .footer {{ background: #212529; color: white; padding: 15px 0; margin-top: 40px; text-align: center; }}
        .nav-link {{ color: white !important; }}
        .navbar-brand {{ color: white !important; font-weight: 700; display: flex; align-items: center; gap: 10px; text-decoration: none; }}
        .logo-img {{ height: 55px; background: white; padding: 5px 15px; border-radius: 60px; }}
        .nav-link.login-btn {{ background: white; color: #E31E24 !important; padding: 5px 20px; border-radius: 20px; font-weight: 600; }}
        .nav-link.login-btn:hover {{ background: #f0f0f0; }}
        .brand-text {{ color: white; font-size: 1.3rem; font-weight: 700; margin-left: 5px; }}
        .search-box {{ background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
        .search-box h2 {{ color: #E31E24; margin-bottom: 20px; text-align: center; }}
        .resultado-item {{ border-left: 4px solid #E31E24; margin-bottom: 15px; padding: 12px 20px; background: #f8f9fa; border-radius: 0 8px 8px 0; }}
        .resultado-item .label {{ font-weight: 600; color: #6c757d; font-size: 0.85rem; }}
        .resultado-item .valor {{ font-size: 1.1rem; font-weight: 500; color: #212529; }}
        .valor-frete {{ font-size: 1.5rem; font-weight: 700; color: #E31E24; }}
        .loading {{ text-align: center; padding: 30px; }}
        .loading .spinner {{ animation: spin 1s linear infinite; font-size: 2rem; }}
        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        .search-icon {{ font-size: 3rem; color: #E31E24; margin-bottom: 15px; text-align: center; }}
        .botoes-acao {{ display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin-top: 20px; }}
        .botoes-acao .btn {{ min-width: 180px; }}
        .form-control:focus {{ border-color: #E31E24; box-shadow: 0 0 0 0.2rem rgba(227, 30, 36, 0.25); }}
        .cotacao-numero {{ font-size: 1.1rem; font-weight: 600; color: #E31E24; text-align: center; margin-bottom: 15px; }}
        .observacao {{ font-size: 0.85rem; color: #6c757d; text-align: center; margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 8px; border: 1px solid #ffeeba; }}
        .btn-nova-cotacao {{ background: #6c757d; color: white; border: none; padding: 10px 30px; border-radius: 8px; }}
        .btn-nova-cotacao:hover {{ background: #5a6268; color: white; }}
        .cliente-encontrado {{ background: #d4edda; color: #155724; padding: 10px 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #c3e6cb; }}
        .info-cliente {{ background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 10px 0; }}
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

    <main class="container py-4">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                <div class="search-box">
                    <div class="search-icon"><i class="bi bi-calculator"></i></div>
                    <h2>SIMULAR FRETE</h2>
                    
                    <form id="formSimulador">
                        <div class="mb-3">
                            <label class="form-label fw-bold">Dados do Cliente</label>
                            <div class="input-group">
                                <input type="text" class="form-control" placeholder="CPF/CNPJ" id="cpfCliente">
                                <button class="btn btn-jadlog" type="button" onclick="buscarCliente()"><i class="bi bi-search"></i> Buscar</button>
                            </div>
                            <div id="infoCliente" style="display: none;" class="mt-2"></div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label fw-bold">Origem</label>
                            <input type="text" class="form-control" value="Bras - SP (03000-000)" readonly disabled>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label fw-bold">CEP de Destino</label>
                            <input type="text" class="form-control form-control-lg" placeholder="Ex: 01000-000" id="cepDestino" required>
                            <small class="text-muted">Ex: 01000-000 (SP Capital) ou 69945-000 (Interior)</small>
                        </div>
                        
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Peso (kg)</label>
                                <input type="number" class="form-control form-control-lg" placeholder="Ex: 2.350" id="peso" step="0.001" required>
                                <small class="text-muted">Ex: 2.350</small>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold">Valor da NF (R$)</label>
                                <input type="number" class="form-control form-control-lg" placeholder="Ex: 5000.00" id="valorNF" step="0.01" required>
                                <small class="text-muted">Seguro: 0,66% do valor da NF (se NF > R$ 100)</small>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <label class="form-label fw-bold">Modalidade</label>
                            <select class="form-control form-control-lg" id="modalidade">
                                <option value="PACKAGE">PACKAGE</option>
                                <option value=".COM">.COM</option>
                            </select>
                            <small class="text-muted">Selecione a modalidade desejada</small>
                        </div>
                        
                        <div class="mt-4">
                            <button type="button" class="btn btn-jadlog btn-lg w-100" onclick="calcularFrete()">
                                <i class="bi bi-calculator"></i> Calcular Frete
                            </button>
                        </div>
                    </form>
                    
                    <div id="resultado" class="mt-4"></div>
                    <div id="areaBotoes" style="display: none;"></div>
                </div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">&copy; 2026 JADLOG BRÁS</div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const NUMERO_COTACAO = '{num_cotacao}';
        let dadosCotacao = null;
        const USUARIO_LOGADO = {'true' if logado else 'false'};
        
        function buscarCliente() {{
            const cpf = document.getElementById('cpfCliente').value.trim();
            const infoDiv = document.getElementById('infoCliente');
            if (!cpf) {{
                infoDiv.style.display = 'block';
                infoDiv.innerHTML = '<div class="alert alert-warning">Digite um CPF/CNPJ para buscar.</div>';
                return;
            }}
            infoDiv.style.display = 'block';
            infoDiv.innerHTML = `
                <div class="cliente-encontrado">
                    <i class="bi bi-check-circle"></i> Cliente encontrado! Dados carregados automaticamente.
                </div>
                <div class="info-cliente">
                    <div><strong>Bruno Henrique Fagundes de Almeida</strong></div>
                    <div class="text-muted">Guarulhos/SP • 11987437462</div>
                </div>
            `;
        }}
        
        function calcularFrete() {{
            const cep = document.getElementById('cepDestino').value.trim();
            const peso = parseFloat(document.getElementById('peso').value);
            const valorNF = parseFloat(document.getElementById('valorNF').value);
            const modalidade = document.getElementById('modalidade').value;
            const resultado = document.getElementById('resultado');
            
            if (!cep || !peso || !valorNF) {{
                resultado.innerHTML = '<div class="alert alert-warning">Preencha todos os campos.</div>';
                return;
            }}
            
            resultado.innerHTML = `<div class="loading"><div class="spinner">⏳</div><p class="mt-2">Simulando frete...</p></div>`;
            document.getElementById('areaBotoes').style.display = 'none';
            
            fetch(`/api/simular?cep=${{encodeURIComponent(cep)}}&peso=${{peso}}&modalidade=${{modalidade}}&valor_nf=${{valorNF}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        const dados = data.dados || data;
                        dadosCotacao = dados;
                        exibirResultado(dados);
                        const areaBotoes = document.getElementById('areaBotoes');
                        areaBotoes.style.display = 'block';
                        areaBotoes.innerHTML = gerarBotoes();
                    }} else {{
                        resultado.innerHTML = `<div class="alert alert-danger">${{data.erro || 'Erro ao simular frete'}}</div>`;
                    }}
                }})
                .catch(() => {{
                    resultado.innerHTML = '<div class="alert alert-warning"><i class="bi bi-exclamation-triangle"></i> Erro ao simular frete. Tente novamente.</div>';
                }});
        }}
        
        function exibirResultado(data) {{
            const seguro = data.seguro || 0;
            const freteTotal = data.total || data.preco_final || data.frete || 0;
            const valorFrete = data.preco_final || data.frete || 0;
            const tipoTarifa = data.tipo_tarifa || 'INTERIOR 1';
            const prazo = data.prazo || 6;
            
            document.getElementById('resultado').innerHTML = `
                <div class="card card-shadow mt-3 text-start">
                    <div class="cotacao-numero"><i class="bi bi-file-text"></i> ${{NUMERO_COTACAO}}</div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="resultado-item"><div class="label">Origem</div><div class="valor">Bras - SP</div></div>
                            <div class="resultado-item"><div class="label">Destino</div><div class="valor">${{data.cidade || 'FRANCO DA ROCHA'}}/${{data.uf || 'SP'}}</div></div>
                            <div class="resultado-item"><div class="label">Prazo</div><div class="valor">${{prazo}} dias</div></div>
                        </div>
                        <div class="col-md-6">
                            <div class="resultado-item"><div class="label">Tipo</div><div class="valor">${{tipoTarifa}}</div></div>
                            <div class="resultado-item"><div class="label">Peso</div><div class="valor">${{data.peso || 10}} kg</div></div>
                            <div class="resultado-item"><div class="label">Modalidade</div><div class="valor">${{data.modalidade || 'PACKAGE'}}</div></div>
                        </div>
                    </div>
                    <hr>
                    <div class="row">
                        <div class="col-md-4"><div class="resultado-item"><div class="label">Valor do Frete</div><div class="valor valor-frete">R$ ${{valorFrete.toFixed(2)}}</div></div></div>
                        <div class="col-md-4"><div class="resultado-item"><div class="label">Seguro</div><div class="valor">R$ ${{seguro.toFixed(2)}}</div></div></div>
                        <div class="col-md-4"><div class="resultado-item" style="border-left-color: #28a745;"><div class="label">Frete Total</div><div class="valor valor-frete" style="color: #28a745;">R$ ${{freteTotal.toFixed(2)}}</div></div></div>
                    </div>
                    <div class="observacao"><i class="bi bi-info-circle"></i> VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRÁS)<br><strong>Validos até Dezembro de 2026</strong></div>
                </div>
            `;
        }}
        
        function gerarBotoes() {{
            const logado = USUARIO_LOGADO;
            let html = '<div class="botoes-acao">';
            if (logado) html += `<button class="btn btn-jadlog" onclick="imprimirCotacao()"><i class="bi bi-printer"></i> Imprimir Recibo</button>`;
            html += `<button class="btn btn-jadlog-outline" onclick="baixarCotacao()"><i class="bi bi-download"></i> Baixar Cotação</button>
                     <button class="btn btn-nova-cotacao" onclick="novaCotacao()"><i class="bi bi-plus-circle"></i> Nova Cotação</button></div>`;
            return html;
        }}
        
        function novaCotacao() {{
            document.getElementById('cepDestino').value = '';
            document.getElementById('peso').value = '';
            document.getElementById('valorNF').value = '';
            document.getElementById('resultado').innerHTML = '';
            document.getElementById('areaBotoes').style.display = 'none';
        }}
        
        function imprimirCotacao() {{
            if (!dadosCotacao) {{ alert('Nenhuma cotação encontrada.'); return; }}
            const janela = window.open('', '_blank', 'width=800,height=600');
            janela.document.write(gerarHTML(dadosCotacao));
            janela.document.close();
            janela.focus();
            janela.print();
            janela.close();
        }}
        
        function baixarCotacao() {{
            if (!dadosCotacao) {{ alert('Nenhuma cotação encontrada.'); return; }}
            const blob = new Blob([gerarHTML(dadosCotacao)], {{ type: 'text/html' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Cotacao_${{dadosCotacao.cep || 'CEP'}}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
        
        function gerarHTML(data) {{
            const seguro = data.seguro || 0;
            const freteTotal = data.total || data.preco_final || data.frete || 0;
            const valorFrete = data.preco_final || data.frete || 0;
            const tipoTarifa = data.tipo_tarifa || 'INTERIOR 1';
            const prazo = data.prazo || 6;
            return `<!DOCTYPE html><html><head><title>Cotação de Frete</title><meta charset="UTF-8"><style>body{{font-family:Arial;padding:20px}}.header{{text-align:center;border-bottom:2px solid #E31E24;padding-bottom:10px}}.header h1{{color:#E31E24}}.cotacao-numero{{text-align:center;font-weight:bold;color:#E31E24;margin:10px 0}}.info{{background:#f5f5f5;padding:15px;border-radius:5px}}.detalhes{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}.detalhes-item{{padding:8px;border-left:3px solid #E31E24}}.frete-total{{font-size:1.8rem;font-weight:bold;color:#28a745;text-align:center;padding:15px;background:#f0f8f0;border-radius:8px}}.observacao{{text-align:center;margin-top:15px;padding:10px;background:#fff3cd;border-radius:8px}}.footer{{text-align:center;margin-top:30px;font-size:12px;color:#999}}</style></head><body><div class="header"><h1>JADLOG BRÁS</h1><h2>Cotação de Frete</h2></div><div class="cotacao-numero">${{NUMERO_COTACAO}}</div><div class="info"><div>Data: ${{new Date().toLocaleString('pt-BR')}}</div><div>CEP: ${{data.cep}}</div><div>Peso: ${{data.peso}} kg</div><div>Modalidade: ${{data.modalidade}}</div></div><div class="detalhes"><div class="detalhes-item"><strong>Origem</strong><br>Bras - SP</div><div class="detalhes-item"><strong>Destino</strong><br>${{data.cidade || 'FRANCO DA ROCHA'}}/${{data.uf || 'SP'}}</div><div class="detalhes-item"><strong>Tipo</strong><br>${{tipoTarifa}}</div><div class="detalhes-item"><strong>Prazo</strong><br>${{prazo}} dias</div><div class="detalhes-item"><strong>Valor do Frete</strong><br>R$ ${{valorFrete.toFixed(2)}}</div><div class="detalhes-item"><strong>Seguro</strong><br>R$ ${{seguro.toFixed(2)}}</div></div><div class="frete-total">Frete Total: R$ ${{freteTotal.toFixed(2)}}</div><div class="observacao">VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRÁS)<br><strong>Válidos até Dezembro de 2026</strong></div><div class="footer"><p>JADLOG BRÁS - Sistema de Cotação de Frete</p></div></body></html>`;
        }}
    </script>
</body>
</html>
    """)