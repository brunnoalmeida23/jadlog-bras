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
        .btn-nova-cotacao {{ background: #6c757d; color: white; border: none; padding: 10px 30px; border-radius: 8px; }}
        .btn-nova-cotacao:hover {{ background: #5a6268; color: white; }}
        
        .card-shadow {{ background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); padding: 24px; }}
        .footer {{ background: #212529; color: white; padding: 15px 0; margin-top: 40px; text-align: center; }}
        .nav-link {{ color: white !important; }}
        .navbar-brand {{ color: white !important; font-weight: 700; display: flex; align-items: center; gap: 10px; text-decoration: none; }}
        .logo-img {{ height: 55px; background: white; padding: 5px 15px; border-radius: 60px; }}
        .nav-link.login-btn {{ background: white; color: #E31E24 !important; padding: 5px 20px; border-radius: 20px; font-weight: 600; }}
        .nav-link.login-btn:hover {{ background: #f0f0f0; }}
        .brand-text {{ color: white; font-size: 1.3rem; font-weight: 700; margin-left: 5px; }}
        
        .search-box {{ 
            background: white; 
            border-radius: 12px; 
            padding: 30px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.08); 
            max-width: 700px; 
            margin: 0 auto;
        }}
        
        .search-box h2 {{ color: #E31E24; margin-bottom: 20px; text-align: center; font-size: 1.3rem; font-weight: 700; }}
        
        .info-item {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .info-item .label {{ font-weight: 600; color: #495057; }}
        .info-item .valor {{ font-weight: 500; color: #212529; }}
        
        .resultado-item {{
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .resultado-item .label {{ font-weight: 600; color: #6c757d; font-size: 0.85rem; }}
        .resultado-item .valor {{ font-size: 1rem; font-weight: 500; color: #212529; }}
        
        .valor-frete {{ font-size: 1.2rem; font-weight: 700; color: #E31E24; }}
        .valor-total {{ font-size: 1.4rem; font-weight: 700; color: #28a745; }}
        
        .loading {{ text-align: center; padding: 30px; }}
        .loading .spinner {{ animation: spin 1s linear infinite; font-size: 2rem; }}
        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        
        .search-icon {{ font-size: 2.5rem; color: #E31E24; margin-bottom: 15px; text-align: center; }}
        
        .botoes-acao {{ display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin-top: 20px; }}
        .botoes-acao .btn {{ min-width: 140px; }}
        
        .form-control:focus {{ border-color: #E31E24; box-shadow: 0 0 0 0.2rem rgba(227, 30, 36, 0.25); }}
        
        .cotacao-numero {{ font-size: 1rem; font-weight: 600; color: #E31E24; margin-bottom: 15px; }}
        
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
        
        .cliente-encontrado {{ 
            background: #d4edda; 
            color: #155724; 
            padding: 8px 12px; 
            border-radius: 6px; 
            margin: 8px 0; 
            border: 1px solid #c3e6cb; 
            font-size: 0.9rem;
        }}
        
        .info-cliente {{ 
            background: #f8f9fa; 
            border-radius: 6px; 
            padding: 10px 15px; 
            margin: 8px 0; 
            border: 1px solid #dee2e6;
        }}
        
        .info-cliente .nome {{ font-weight: 600; font-size: 1rem; }}
        .info-cliente .detalhes {{ color: #6c757d; font-size: 0.85rem; }}
        
        .campo-origem {{ background: #e9ecef; cursor: not-allowed; }}
        
        .dados-cliente {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        
        .dados-cliente .cpf {{
            font-size: 0.9rem;
            color: #6c757d;
        }}
        
        .resultado-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        
        @media (max-width: 600px) {{
            .resultado-grid {{
                grid-template-columns: 1fr;
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

    <main class="container py-4">
        <div class="search-box">
            <div class="search-icon"><i class="bi bi-calculator"></i></div>
            <h2>SIMULAR FRETE</h2>
            
            <form id="formSimulador">
                <!-- Dados do Cliente -->
                <div class="dados-cliente">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold">Dados do Cliente</span>
                        <span class="cpf">405.890.958-70</span>
                    </div>
                    <div id="infoCliente">
                        <div class="cliente-encontrado">
                            <i class="bi bi-check-circle"></i> Cliente encontrado! Dados carregados automaticamente.
                        </div>
                        <div class="info-cliente">
                            <div class="nome">Bruno Henrique Fagundes de Almeida</div>
                            <div class="detalhes">Guarulhos/SP • 11987437462</div>
                        </div>
                    </div>
                    <div id="cadastroCliente" style="display: none;"></div>
                </div>
                
                <!-- Origem -->
                <div class="mb-3">
                    <label class="form-label fw-bold">Origem</label>
                    <input type="text" class="form-control campo-origem" value="Bras - SP (03000-000)" readonly disabled>
                </div>
                
                <!-- CEP Destino -->
                <div class="mb-3">
                    <label class="form-label fw-bold">CEP de Destino</label>
                    <input type="text" class="form-control" placeholder="Ex: 01000-000" id="cepDestino" value="07071060">
                    <small class="text-muted">Ex: 01000-000 (SP Capital) ou 69945-000 (Interior)</small>
                </div>
                
                <!-- Peso e Valor NF -->
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Peso (kg)</label>
                        <input type="number" class="form-control" placeholder="Ex: 2.350" id="peso" value="10" step="0.001">
                        <small class="text-muted">Ex: 2.350</small>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-bold">Valor da NF (R$)</label>
                        <input type="number" class="form-control" placeholder="Ex: 5000.00" id="valorNF" value="100" step="0.01">
                        <small class="text-muted">Seguro: 0,66% do valor da NF (se NF > R$ 100)</small>
                    </div>
                </div>
                
                <!-- Modalidade -->
                <div class="mt-3">
                    <label class="form-label fw-bold">Modalidade</label>
                    <select class="form-control" id="modalidade">
                        <option value="PACKAGE">PACKAGE</option>
                        <option value=".COM">.COM</option>
                    </select>
                    <small class="text-muted">Selecione a modalidade desejada</small>
                </div>
                
                <div class="mt-4">
                    <button type="button" class="btn btn-jadlog w-100" onclick="calcularFrete()" style="padding: 12px; font-size: 1.1rem;">
                        <i class="bi bi-calculator"></i> Calcular Frete
                    </button>
                </div>
            </form>
            
            <!-- Resultado -->
            <div id="resultado" class="mt-4">
                <div class="card card-shadow">
                    <div class="cotacao-numero"><i class="bi bi-file-text"></i> COT-2026-0806-1109</div>
                    
                    <div class="resultado-grid">
                        <div>
                            <div class="resultado-item"><div class="label">Origem</div><div class="valor">Bras - SP</div></div>
                            <div class="resultado-item"><div class="label">Destino</div><div class="valor">FRANCO DA ROCHA/SP</div></div>
                            <div class="resultado-item"><div class="label">Prazo</div><div class="valor">4 dias</div></div>
                            <div class="resultado-item"><div class="label">Modalidade</div><div class="valor">PACKAGE</div></div>
                        </div>
                        <div>
                            <div class="resultado-item"><div class="label">Tipo</div><div class="valor">Capital</div></div>
                            <div class="resultado-item"><div class="label">Peso</div><div class="valor">10 kg</div></div>
                            <div class="resultado-item"><div class="label">Valor do Frete</div><div class="valor valor-frete">R$ 123.99</div></div>
                            <div class="resultado-item"><div class="label">Seguro</div><div class="valor">R$ 0.00</div></div>
                        </div>
                    </div>
                    
                    <div class="text-center mt-3" style="border-top: 2px solid #E31E24; padding-top: 15px;">
                        <span style="font-size: 1.4rem; font-weight: 700; color: #28a745;">Frete Total: R$ 123.99</span>
                    </div>
                    
                    <div class="observacao">
                        <i class="bi bi-info-circle"></i> VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRÁS)<br>
                        <strong>Validos até Dezembro de 2026</strong>
                    </div>
                </div>
            </div>
            
            <div id="areaBotoes" class="mt-3">
                <div class="botoes-acao">
                    <button class="btn btn-jadlog" onclick="imprimirCotacao()"><i class="bi bi-printer"></i> Imprimir Recibo</button>
                    <button class="btn btn-jadlog-outline" onclick="baixarCotacao()"><i class="bi bi-download"></i> Baixar Cotação</button>
                    <button class="btn btn-nova-cotacao" onclick="novaCotacao()"><i class="bi bi-plus-circle"></i> Nova Cotação</button>
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
        const USUARIO_LOGADO = {'true' if logado else 'false'};
        let dadosCotacao = null;
        
        function calcularFrete() {{
            const cep = document.getElementById('cepDestino').value.trim();
            const peso = parseFloat(document.getElementById('peso').value);
            const valorNF = parseFloat(document.getElementById('valorNF').value);
            const modalidade = document.getElementById('modalidade').value;
            const resultado = document.getElementById('resultado');
            
            if (!cep || !peso || !valorNF) {{
                resultado.innerHTML = '<div class="alert alert-warning mt-3">Preencha todos os campos.</div>';
                return;
            }}
            
            resultado.innerHTML = `<div class="loading mt-3"><div class="spinner">⏳</div><p class="mt-2">Simulando frete...</p></div>`;
            
            fetch(`/api/simular?cep=${{encodeURIComponent(cep)}}&peso=${{peso}}&modalidade=${{modalidade}}&valor_nf=${{valorNF}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        const dados = data.dados || data;
                        dadosCotacao = dados;
                        exibirResultado(dados);
                    }} else {{
                        resultado.innerHTML = `<div class="alert alert-danger mt-3">${{data.erro || 'Erro ao simular frete'}}</div>`;
                    }}
                }})
                .catch(() => {{
                    resultado.innerHTML = '<div class="alert alert-warning mt-3"><i class="bi bi-exclamation-triangle"></i> Erro ao simular frete. Tente novamente.</div>';
                }});
        }}
        
        function exibirResultado(data) {{
            const seguro = data.seguro || 0;
            const freteTotal = data.total || data.preco_final || data.frete || 0;
            const valorFrete = data.preco_final || data.frete || 0;
            const tipoTarifa = data.tipo_tarifa || 'Capital';
            const prazo = data.prazo || 4;
            const cidade = data.cidade || 'GUARULHOS';
            const uf = data.uf || 'SP';
            const modalidade = data.modalidade || 'PACKAGE';
            
            document.getElementById('resultado').innerHTML = `
                <div class="card card-shadow mt-3">
                    <div class="cotacao-numero"><i class="bi bi-file-text"></i> ${{NUMERO_COTACAO}}</div>
                    
                    <div class="resultado-grid">
                        <div>
                            <div class="resultado-item"><div class="label">Origem</div><div class="valor">Bras - SP</div></div>
                            <div class="resultado-item"><div class="label">Destino</div><div class="valor">${{cidade}}/${{uf}}</div></div>
                            <div class="resultado-item"><div class="label">Prazo</div><div class="valor">${{prazo}} dias</div></div>
                            <div class="resultado-item"><div class="label">Modalidade</div><div class="valor">${{modalidade}}</div></div>
                        </div>
                        <div>
                            <div class="resultado-item"><div class="label">Tipo</div><div class="valor">${{tipoTarifa}}</div></div>
                            <div class="resultado-item"><div class="label">Peso</div><div class="valor">${{data.peso || 10}} kg</div></div>
                            <div class="resultado-item"><div class="label">Valor do Frete</div><div class="valor valor-frete">R$ ${{valorFrete.toFixed(2)}}</div></div>
                            <div class="resultado-item"><div class="label">Seguro</div><div class="valor">R$ ${{seguro.toFixed(2)}}</div></div>
                        </div>
                    </div>
                    
                    <div class="text-center mt-3" style="border-top: 2px solid #E31E24; padding-top: 15px;">
                        <span style="font-size: 1.4rem; font-weight: 700; color: #28a745;">Frete Total: R$ ${{freteTotal.toFixed(2)}}</span>
                    </div>
                    
                    <div class="observacao">
                        <i class="bi bi-info-circle"></i> VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRÁS)<br>
                        <strong>Validos até Dezembro de 2026</strong>
                    </div>
                </div>
            `;
        }}
        
        function novaCotacao() {{
            document.getElementById('cepDestino').value = '';
            document.getElementById('peso').value = '';
            document.getElementById('valorNF').value = '';
            document.getElementById('resultado').innerHTML = '';
            document.getElementById('cepDestino').focus();
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
            const tipoTarifa = data.tipo_tarifa || 'Capital';
            const prazo = data.prazo || 4;
            const cidade = data.cidade || 'GUARULHOS';
            const uf = data.uf || 'SP';
            const modalidade = data.modalidade || 'PACKAGE';
            
            return `<!DOCTYPE html><html><head><title>Cotação de Frete - JADLOG BRÁS</title><meta charset="UTF-8"><style>
                body{{font-family:Arial;padding:20px;max-width:700px;margin:0 auto}}
                .header{{text-align:center;border-bottom:2px solid #E31E24;padding-bottom:10px}}
                .header h1{{color:#E31E24;margin:0}}
                .cotacao-numero{{text-align:center;font-weight:bold;color:#E31E24;margin:15px 0}}
                .info{{background:#f5f5f5;padding:15px;border-radius:5px;margin-bottom:15px}}
                .info-item{{margin:5px 0}}
                .info-item .label{{font-weight:bold}}
                .grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:15px 0}}
                .item{{padding:8px;border-left:3px solid #E31E24}}
                .total{{font-size:1.6rem;font-weight:bold;color:#28a745;text-align:center;padding:15px;background:#f0f8f0;border-radius:8px;margin:15px 0}}
                .obs{{text-align:center;padding:10px;background:#fff3cd;border-radius:8px;border:1px solid #ffeeba;font-size:0.9rem;margin:15px 0}}
                .footer{{text-align:center;margin-top:30px;font-size:12px;color:#999}}
            </style></head><body>
                <div class="header"><h1>JADLOG BRÁS</h1><h2>Cotação de Frete</h2></div>
                <div class="cotacao-numero">${{NUMERO_COTACAO}}</div>
                <div class="info">
                    <div class="info-item"><span class="label">Data:</span> ${{new Date().toLocaleString('pt-BR')}}</div>
                    <div class="info-item"><span class="label">CEP:</span> ${{data.cep || 'N/A'}}</div>
                    <div class="info-item"><span class="label">Peso:</span> ${{data.peso || 'N/A'}} kg</div>
                </div>
                <div class="grid">
                    <div class="item"><strong>Origem</strong><br>Bras - SP</div>
                    <div class="item"><strong>Destino</strong><br>${{cidade}}/${{uf}}</div>
                    <div class="item"><strong>Tipo</strong><br>${{tipoTarifa}}</div>
                    <div class="item"><strong>Prazo</strong><br>${{prazo}} dias</div>
                    <div class="item"><strong>Modalidade</strong><br>${{modalidade}}</div>
                    <div class="item"><strong>Peso</strong><br>${{data.peso || 10}} kg</div>
                    <div class="item"><strong>Valor Frete</strong><br>R$ ${{valorFrete.toFixed(2)}}</div>
                    <div class="item"><strong>Seguro</strong><br>R$ ${{seguro.toFixed(2)}}</div>
                </div>
                <div class="total">Frete Total: R$ ${{freteTotal.toFixed(2)}}</div>
                <div class="obs">VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRÁS)<br><strong>Válidos até Dezembro de 2026</strong></div>
                <div class="footer"><p>JADLOG BRÁS - Sistema de Cotação de Frete</p></div>
            </body></html>`;
        }}
    </script>
</body>
</html>
    """)