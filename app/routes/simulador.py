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
        .btn-jadlog {{ background: #E31E24; color: white; border: none; padding: 10px 20px; border-radius: 8px; }}
        .btn-jadlog:hover {{ background: #B81217; color: white; }}
        .btn-jadlog-outline {{ background: transparent; color: #E31E24; border: 2px solid #E31E24; padding: 10px 20px; border-radius: 8px; }}
        .btn-jadlog-outline:hover {{ background: #E31E24; color: white; }}
        .btn-nova-cotacao {{ background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 8px; }}
        .btn-nova-cotacao:hover {{ background: #5a6268; color: white; }}
        .btn-sm-custom {{ padding: 8px 16px; font-size: 0.9rem; }}
        
        .footer {{ background: #212529; color: white; padding: 15px 0; margin-top: 40px; text-align: center; }}
        .nav-link {{ color: white !important; }}
        .navbar-brand {{ color: white !important; font-weight: 700; display: flex; align-items: center; gap: 10px; text-decoration: none; }}
        .logo-img {{ height: 55px; background: white; padding: 5px 15px; border-radius: 60px; }}
        .nav-link.login-btn {{ background: white; color: #E31E24 !important; padding: 5px 20px; border-radius: 20px; font-weight: 600; }}
        .nav-link.login-btn:hover {{ background: #f0f0f0; }}
        .brand-text {{ color: white; font-size: 1.3rem; font-weight: 700; margin-left: 5px; }}
        
        .main-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .left-column {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        
        .right-column {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        
        .right-column .titulo-recibo {{
            color: #E31E24;
            font-size: 1.1rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 15px;
        }}
        
        .right-column .cotacao-numero {{
            text-align: center;
            font-weight: 600;
            color: #E31E24;
            margin-bottom: 15px;
            font-size: 0.95rem;
        }}
        
        .linha-recibo {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .linha-recibo .label {{
            font-weight: 600;
            color: #495057;
            font-size: 0.85rem;
        }}
        
        .linha-recibo .valor {{
            font-weight: 500;
            color: #212529;
            font-size: 0.85rem;
        }}
        
        .linha-recibo .valor-frete {{
            font-weight: 700;
            color: #E31E24;
            font-size: 1rem;
        }}
        
        .linha-recibo .valor-total {{
            font-weight: 700;
            color: #28a745;
            font-size: 1.2rem;
        }}
        
        .recibo-observacao {{
            font-size: 0.75rem;
            color: #6c757d;
            text-align: center;
            margin-top: 15px;
            padding: 10px;
            background: #fff3cd;
            border-radius: 8px;
            border: 1px solid #ffeeba;
        }}
        
        .recibo-observacao strong {{
            color: #856404;
        }}
        
        .botoes-recibo {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        
        .botoes-recibo .btn {{
            min-width: 130px;
        }}
        
        .form-label {{
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        .form-control:focus {{
            border-color: #E31E24;
            box-shadow: 0 0 0 0.2rem rgba(227, 30, 36, 0.25);
        }}
        
        .cliente-encontrado {{
            background: #d4edda;
            color: #155724;
            padding: 6px 12px;
            border-radius: 6px;
            margin: 5px 0;
            border: 1px solid #c3e6cb;
            font-size: 0.85rem;
        }}
        
        .info-cliente {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 10px 15px;
            margin: 5px 0;
            border: 1px solid #dee2e6;
        }}
        
        .info-cliente .nome {{ font-weight: 600; font-size: 0.95rem; }}
        .info-cliente .detalhes {{ color: #6c757d; font-size: 0.8rem; }}
        
        .campo-origem {{ background: #e9ecef; cursor: not-allowed; }}
        
        .recibo-vazio {{
            text-align: center;
            color: #999;
            padding: 40px 0;
        }}
        
        .recibo-vazio i {{
            font-size: 3rem;
            color: #ddd;
        }}
        
        @media (max-width: 768px) {{
            .left-column, .right-column {{
                margin-bottom: 20px;
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
        <div class="row g-4">
            <!-- COLUNA ESQUERDA - FORMULÁRIO -->
            <div class="col-lg-5">
                <div class="left-column">
                    <h5 style="color: #E31E24; font-weight: 700; margin-bottom: 20px;">
                        <i class="bi bi-calculator"></i> SIMULAR FRETE
                    </h5>
                    
                    <form id="formSimulador">
                        <!-- Cliente -->
                        <div class="mb-3">
                            <label class="form-label">Dados do Cliente</label>
                            <div class="input-group input-group-sm">
                                <input type="text" class="form-control" placeholder="CPF/CNPJ" id="cpfCliente" value="405.890.958-70">
                                <button class="btn btn-jadlog btn-sm" type="button" onclick="buscarCliente()">
                                    <i class="bi bi-search"></i>
                                </button>
                            </div>
                            <div id="infoCliente" class="mt-2">
                                <div class="cliente-encontrado">
                                    <i class="bi bi-check-circle"></i> Cliente encontrado!
                                </div>
                                <div class="info-cliente">
                                    <div class="nome">Bruno Henrique Fagundes de Almeida</div>
                                    <div class="detalhes">Guarulhos/SP • 11987437462</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Origem -->
                        <div class="mb-3">
                            <label class="form-label">Origem</label>
                            <input type="text" class="form-control form-control-sm campo-origem" value="Bras - SP (03000-000)" readonly disabled>
                        </div>
                        
                        <!-- CEP -->
                        <div class="mb-3">
                            <label class="form-label">CEP de Destino</label>
                            <input type="text" class="form-control form-control-sm" placeholder="Ex: 01000-000" id="cepDestino" value="07071060">
                            <small class="text-muted" style="font-size: 0.7rem;">Ex: 01000-000 (SP Capital) ou 69945-000 (Interior)</small>
                        </div>
                        
                        <!-- Peso e Valor NF -->
                        <div class="row g-2">
                            <div class="col-6">
                                <label class="form-label">Peso (kg)</label>
                                <input type="number" class="form-control form-control-sm" placeholder="Ex: 2.350" id="peso" value="10" step="0.001">
                                <small class="text-muted" style="font-size: 0.7rem;">Ex: 2.350</small>
                            </div>
                            <div class="col-6">
                                <label class="form-label">Valor NF (R$)</label>
                                <input type="number" class="form-control form-control-sm" placeholder="Ex: 5000.00" id="valorNF" value="100" step="0.01">
                                <small class="text-muted" style="font-size: 0.7rem;">Seguro: 0,66% se NF > R$ 100</small>
                            </div>
                        </div>
                        
                        <!-- Modalidade -->
                        <div class="mt-3">
                            <label class="form-label">Modalidade</label>
                            <select class="form-control form-control-sm" id="modalidade">
                                <option value="PACKAGE">PACKAGE</option>
                                <option value=".COM">.COM</option>
                            </select>
                            <small class="text-muted" style="font-size: 0.7rem;">Selecione a modalidade desejada</small>
                        </div>
                        
                        <div class="mt-3">
                            <button type="button" class="btn btn-jadlog w-100 btn-sm-custom" onclick="calcularFrete()">
                                <i class="bi bi-calculator"></i> Calcular Frete
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- COLUNA DIREITA - RECIBO -->
            <div class="col-lg-7">
                <div class="right-column" id="reciboContainer">
                    <div class="titulo-recibo">
                        <i class="bi bi-file-text"></i> RECIBO DE COTAÇÃO
                    </div>
                    
                    <div id="reciboConteudo">
                        <!-- Recibo vazio (será preenchido pelo JavaScript) -->
                        <div class="recibo-vazio" id="reciboVazio">
                            <i class="bi bi-receipt"></i>
                            <p class="mt-2">Preencha os dados e clique em<br><strong>"Calcular Frete"</strong></p>
                        </div>
                        
                        <!-- Recibo com dados (oculto inicialmente) -->
                        <div id="reciboPreenchido" style="display: none;">
                            <div class="cotacao-numero" id="reciboNumero">COT-2026-0806-1109</div>
                            
                            <div id="reciboLinhas">
                                <!-- Preenchido pelo JavaScript -->
                            </div>
                            
                            <div class="recibo-observacao">
                                <i class="bi bi-info-circle"></i> VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRÁS)<br>
                                <strong>Válidos até Dezembro de 2026</strong>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Botões do recibo -->
                    <div class="botoes-recibo" id="botoesRecibo" style="display: none;">
                        <button class="btn btn-jadlog btn-sm" onclick="imprimirCotacao()">
                            <i class="bi bi-printer"></i> Imprimir
                        </button>
                        <button class="btn btn-jadlog-outline btn-sm" onclick="baixarCotacao()">
                            <i class="bi bi-download"></i> Baixar
                        </button>
                        <button class="btn btn-nova-cotacao btn-sm" onclick="novaCotacao()">
                            <i class="bi bi-plus-circle"></i> Nova
                        </button>
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
        const NUMERO_COTACAO = '{num_cotacao}';
        const USUARIO_LOGADO = {'true' if logado else 'false'};
        let dadosCotacao = null;
        
        function buscarCliente() {{
            // Função já integrada ao formulário
        }}
        
        function calcularFrete() {{
            const cep = document.getElementById('cepDestino').value.trim();
            const peso = parseFloat(document.getElementById('peso').value);
            const valorNF = parseFloat(document.getElementById('valorNF').value);
            const modalidade = document.getElementById('modalidade').value;
            
            if (!cep || !peso || !valorNF) {{
                alert('Preencha todos os campos.');
                return;
            }}
            
            document.getElementById('reciboVazio').style.display = 'none';
            document.getElementById('reciboPreenchido').style.display = 'block';
            document.getElementById('reciboPreenchido').innerHTML = '<div class="text-center p-4"><div class="spinner-border text-danger" role="status"></div><p class="mt-2">Calculando...</p></div>';
            
            fetch(`/api/simular?cep=${{encodeURIComponent(cep)}}&peso=${{peso}}&modalidade=${{modalidade}}&valor_nf=${{valorNF}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        const dados = data.dados || data;
                        dadosCotacao = dados;
                        exibirRecibo(dados);
                        document.getElementById('botoesRecibo').style.display = 'flex';
                    }} else {{
                        alert(data.erro || 'Erro ao calcular frete');
                    }}
                }})
                .catch(() => {{
                    alert('Erro ao calcular frete. Tente novamente.');
                }});
        }}
        
        function exibirRecibo(data) {{
            const seguro = data.seguro || 0;
            const freteTotal = data.total || data.preco_final || data.frete || 0;
            const valorFrete = data.preco_final || data.frete || 0;
            const tipoTarifa = data.tipo_tarifa || 'Capital';
            const prazo = data.prazo || 4;
            const cidade = data.cidade || 'GUARULHOS';
            const uf = data.uf || 'SP';
            const modalidade = data.modalidade || 'PACKAGE';
            
            let linhas = '';
            const itens = [
                ['Origem', 'Bras - SP'],
                ['Destino', cidade + '/' + uf],
                ['Prazo', prazo + ' dias'],
                ['Modalidade', modalidade],
                ['Tipo', tipoTarifa],
                ['Peso', (data.peso || 10) + ' kg'],
                ['Valor do Frete', 'R$ ' + valorFrete.toFixed(2)],
                ['Seguro', 'R$ ' + seguro.toFixed(2)]
            ];
            
            itens.forEach(item => {{
                const classe = item[0] === 'Valor do Frete' ? 'valor-frete' : 
                              item[0] === 'Seguro' ? '' : '';
                linhas += `
                    <div class="linha-recibo">
                        <span class="label">${{item[0]}}</span>
                        <span class="valor ${{classe}}">${{item[1]}}</span>
                    </div>
                `;
            }});
            
            linhas += `
                <div class="linha-recibo" style="border-bottom: 2px solid #E31E24; padding-top: 10px; margin-top: 5px;">
                    <span class="label" style="font-size: 1rem;">Frete Total</span>
                    <span class="valor valor-total">R$ ${{freteTotal.toFixed(2)}}</span>
                </div>
            `;
            
            document.getElementById('reciboPreenchido').innerHTML = `
                <div class="cotacao-numero">${{NUMERO_COTACAO}}</div>
                ${{linhas}}
                <div class="recibo-observacao">
                    <i class="bi bi-info-circle"></i> VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRÁS)<br>
                    <strong>Válidos até Dezembro de 2026</strong>
                </div>
            `;
        }}
        
        function novaCotacao() {{
            document.getElementById('cepDestino').value = '';
            document.getElementById('peso').value = '';
            document.getElementById('valorNF').value = '';
            document.getElementById('reciboPreenchido').style.display = 'none';
            document.getElementById('reciboVazio').style.display = 'block';
            document.getElementById('botoesRecibo').style.display = 'none';
            dadosCotacao = null;
            document.getElementById('cepDestino').focus();
        }}
        
        function imprimirCotacao() {{
            if (!dadosCotacao) {{ alert('Nenhuma cotação para imprimir.'); return; }}
            const janela = window.open('', '_blank', 'width=800,height=600');
            janela.document.write(gerarHTMLRecibo(dadosCotacao));
            janela.document.close();
            janela.focus();
            janela.print();
            janela.close();
        }}
        
        function baixarCotacao() {{
            if (!dadosCotacao) {{ alert('Nenhuma cotação para baixar.'); return; }}
            const blob = new Blob([gerarHTMLRecibo(dadosCotacao)], {{ type: 'text/html' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Cotacao_${{dadosCotacao.cep || 'CEP'}}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
        
        function gerarHTMLRecibo(data) {{
            const seguro = data.seguro || 0;
            const freteTotal = data.total || data.preco_final || data.frete || 0;
            const valorFrete = data.preco_final || data.frete || 0;
            const tipoTarifa = data.tipo_tarifa || 'Capital';
            const prazo = data.prazo || 4;
            const cidade = data.cidade || 'GUARULHOS';
            const uf = data.uf || 'SP';
            const modalidade = data.modalidade || 'PACKAGE';
            
            return `<!DOCTYPE html>
            <html>
            <head><title>Cotação - JADLOG BRÁS</title>
            <meta charset="UTF-8">
            <style>
                body{{font-family:Arial;padding:30px;max-width:600px;margin:0 auto}}
                .header{{text-align:center;border-bottom:2px solid #E31E24;padding-bottom:10px}}
                .header h1{{color:#E31E24;margin:0;font-size:1.5rem}}
                .header h2{{font-size:1.1rem;color:#555;margin:5px 0}}
                .numero{{text-align:center;font-weight:bold;color:#E31E24;margin:15px 0;font-size:1rem}}
                .linha{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #eee}}
                .label{{font-weight:bold;color:#555}}
                .valor{{font-weight:500}}
                .total{{font-size:1.3rem;font-weight:bold;color:#28a745;text-align:center;padding:15px;background:#f0f8f0;border-radius:8px;margin:15px 0}}
                .obs{{text-align:center;padding:10px;background:#fff3cd;border-radius:8px;border:1px solid #ffeeba;font-size:0.8rem;margin:15px 0}}
                .footer{{text-align:center;margin-top:30px;font-size:11px;color:#999;border-top:1px solid #ddd;padding-top:10px}}
            </style>
            </head>
            <body>
                <div class="header"><h1>JADLOG BRÁS</h1><h2>Cotação de Frete</h2></div>
                <div class="numero">${{NUMERO_COTACAO}}</div>
                <div class="linha"><span class="label">Origem</span><span class="valor">Bras - SP</span></div>
                <div class="linha"><span class="label">Destino</span><span class="valor">${{cidade}}/${{uf}}</span></div>
                <div class="linha"><span class="label">Prazo</span><span class="valor">${{prazo}} dias</span></div>
                <div class="linha"><span class="label">Modalidade</span><span class="valor">${{modalidade}}</span></div>
                <div class="linha"><span class="label">Tipo</span><span class="valor">${{tipoTarifa}}</span></div>
                <div class="linha"><span class="label">Peso</span><span class="valor">${{data.peso || 10}} kg</span></div>
                <div class="linha"><span class="label">Valor do Frete</span><span class="valor">R$ ${{valorFrete.toFixed(2)}}</span></div>
                <div class="linha"><span class="label">Seguro</span><span class="valor">R$ ${{seguro.toFixed(2)}}</span></div>
                <div class="total">Frete Total: R$ ${{freteTotal.toFixed(2)}}</div>
                <div class="obs">VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRÁS)<br><strong>Válidos até Dezembro de 2026</strong></div>
                <div class="footer"><p>JADLOG BRÁS - Sistema de Cotação de Frete</p></div>
            </body>
            </html>`;
        }}
    </script>
</body>
</html>
    """)