# app/routes/simulador.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
import re

from app.services.frete_calculator import FreteCalculator
from app.utils.helpers import gerar_cotacao_id

router = APIRouter(prefix="/simulador", tags=["Simulador"])


@router.get("/", response_class=HTMLResponse)
async def simulador_page():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>JADLOG BRÁS - Simulador</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        .bg-jadlog { background: #E31E24; }
        .btn-jadlog { background: #E31E24; color: white; border: none; padding: 10px 30px; border-radius: 8px; }
        .btn-jadlog:hover { background: #B81217; color: white; }
        .btn-jadlog:disabled { opacity: 0.6; cursor: not-allowed; }
        .card-shadow { background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); padding: 24px; }
        .footer { background: #212529; color: white; padding: 15px 0; margin-top: 40px; text-align: center; }
        .nav-link { color: white !important; }
        .navbar-brand { color: white !important; font-weight: 700; }
        .resultado-box { background: #f8f9fa; padding: 16px; border-radius: 8px; border-left: 4px solid #E31E24; }
        .badge-origem { background: #E31E24; color: white; padding: 8px 16px; border-radius: 20px; font-weight: 600; display: inline-block; }
        .badge-cotacao { background: #28a745; color: white; padding: 8px 16px; border-radius: 20px; font-weight: 600; display: inline-block; cursor: pointer; }
        .modalidade-btn {
            padding: 8px 16px;
            border-radius: 8px;
            border: 2px solid #dee2e6;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
        }
        .modalidade-btn:hover { border-color: #E31E24; }
        .modalidade-btn.active { border-color: #E31E24; background: #E31E24; color: white; }
        .modalidade-btn.active:hover { background: #B81217; }
        .valor-total { font-size: 2rem; font-weight: 800; color: #E31E24; }
        .promocao-bras {
            background: #f8f9fa;
            border: 2px dashed #E31E24;
            border-radius: 8px;
            padding: 10px;
            margin-top: 15px;
            text-align: center;
        }
        .promocao-bras .titulo { color: #E31E24; font-weight: 600; font-size: 0.9rem; }
        .promocao-bras .validade { color: #6c757d; font-size: 0.8rem; }
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
        <h2 class="fw-bold mb-4"><i class="bi bi-calculator text-danger me-2"></i>Simular Frete</h2>

        <div class="row g-4">
            <div class="col-lg-7">
                <div class="card-shadow">
                    <div class="mb-3">
                        <label class="fw-bold">
                            <i class="bi bi-geo-alt me-1"></i>
                            CEP de Destino
                        </label>
                        <input type="text" class="form-control form-control-lg" id="cepDestino" 
                               placeholder="Digite o CEP" maxlength="9" required>
                        <small class="text-muted">Ex: 01000-000 (SP Capital) ou 69945-000 (Interior)</small>
                    </div>
                    
                    <div class="mb-3">
                        <label class="fw-bold">
                            <i class="bi bi-weight-scale me-1"></i>
                            Peso (kg)
                        </label>
                        <input type="number" class="form-control form-control-lg" id="peso" 
                               step="0.001" placeholder="Ex: 2.350" required>
                    </div>
                    
                    <div class="mb-3">
                        <label class="fw-bold">
                            <i class="bi bi-receipt me-1"></i>
                            Valor da NF (R$)
                        </label>
                        <input type="number" class="form-control form-control-lg" id="valorNF" 
                               step="0.01" placeholder="Ex: 5000.00" required>
                        <small class="text-muted">Seguro: 0,66% do valor da NF (se NF > R$ 100)</small>
                    </div>

                    <div class="mb-3">
                        <label class="fw-bold">
                            <i class="bi bi-box-seam me-1"></i>
                            Modalidade
                        </label>
                        <div class="d-flex gap-2">
                            <button type="button" class="modalidade-btn active" id="btnPackage" onclick="selecionarModalidade('PACKAGE')">
                                .PACKAGE
                            </button>
                            <button type="button" class="modalidade-btn" id="btnCom" onclick="selecionarModalidade('.COM')">
                                .COM
                            </button>
                        </div>
                        <small class="text-muted">Selecione a modalidade desejada para o frete</small>
                    </div>

                    <input type="hidden" id="modalidadeSelecionada" value="PACKAGE">
                    
                    <button type="button" class="btn btn-jadlog w-100 mt-3" id="btnCalcular" onclick="calcularFrete()">
                        <i class="bi bi-calculator me-2"></i>
                        Calcular Frete
                    </button>
                </div>
            </div>

            <div class="col-lg-5">
                <div class="card-shadow" id="resultadoArea">
                    <h5 class="fw-bold">
                        <i class="bi bi-file-text text-danger me-2"></i>
                        Resultado da Cotação
                    </h5>
                    <div class="text-center text-muted py-5">
                        <i class="bi bi-search fs-1 d-block mb-3"></i>
                        <p>Preencha os dados ao lado<br>e clique em <strong>Calcular Frete</strong></p>
                    </div>
                </div>
                
                <div class="card-shadow" id="resultadoDados" style="display:none;">
                    <h5 class="fw-bold">
                        <i class="bi bi-file-text text-danger me-2"></i>
                        Resultado da Cotação
                    </h5>
                    <div class="mb-3">
                        <span class="badge-cotacao" id="numeroCotacao">
                            <i class="bi bi-hash me-1"></i>COT-2026-0001
                        </span>
                    </div>
                    <div class="resultado-box">
                        <div class="row">
                            <div class="col-6">
                                <small class="text-muted">Origem</small>
                                <p class="fw-bold mb-0">Brás - SP</p>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Destino</small>
                                <p class="fw-bold mb-0" id="resDestino">-</p>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-6">
                                <small class="text-muted">Tipo</small>
                                <p class="fw-bold mb-0" id="resTipo">-</p>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Prazo</small>
                                <p class="fw-bold mb-0" id="resPrazo">-</p>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-6">
                                <small class="text-muted">Peso</small>
                                <p class="fw-bold mb-0" id="resPeso">-</p>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Modalidade</small>
                                <p class="fw-bold mb-0" id="resModalidade">PACKAGE</p>
                            </div>
                        </div>
                        <hr>
                        <div class="row">
                            <div class="col-6">
                                <small class="text-muted">Valor do Frete</small>
                                <p class="fw-bold text-success fs-5" id="resFrete">R$ -</p>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Seguro</small>
                                <p class="fw-bold" id="resSeguro">R$ -</p>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-12">
                                <small class="text-muted">Frete Total</small>
                                <p class="fw-bold fs-3 text-danger" id="resTotal">R$ -</p>
                            </div>
                        </div>
                        <div class="promocao-bras">
                            <div class="titulo">
                                <i class="bi bi-star-fill text-warning me-1"></i>
                                VALORES EXCLUSIVOS DA UNIDADE DA AV. VAUTIER, 455 (BRÁS)
                            </div>
                            <div class="validade">
                                <i class="bi bi-calendar me-1"></i>
                                Válidos até Dezembro de 2026
                            </div>
                        </div>
                    </div>
                    
                    <button class="btn btn-outline-danger w-100 mt-2" onclick="limparResultado()">
                        <i class="bi bi-arrow-counterclockwise me-2"></i>
                        Nova Cotação
                    </button>
                </div>

                <div id="erroArea" style="display:none;" class="alert alert-danger mt-3"></div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">&copy; 2026 JADLOG BRÁS</div>
    </footer>

    <script>
        // ===== MODALIDADE =====
        function selecionarModalidade(modalidade) {
            document.getElementById('modalidadeSelecionada').value = modalidade;
            document.getElementById('btnPackage').classList.remove('active');
            document.getElementById('btnCom').classList.remove('active');
            if (modalidade === 'PACKAGE') {
                document.getElementById('btnPackage').classList.add('active');
            } else {
                document.getElementById('btnCom').classList.add('active');
            }
        }

        // ===== MÁSCARA CEP =====
        document.getElementById('cepDestino').addEventListener('input', function(e) {
            let value = this.value.replace(/\\D/g, '');
            if (value.length > 5) {
                value = value.substring(0, 5) + '-' + value.substring(5, 8);
            }
            this.value = value;
        });

        // ===== CALCULAR FRETE =====
        async function calcularFrete() {
            const btn = document.getElementById('btnCalcular');
            const cep = document.getElementById('cepDestino').value;
            const peso = document.getElementById('peso').value;
            const valorNF = document.getElementById('valorNF').value;
            const modalidade = document.getElementById('modalidadeSelecionada').value;
            
            // Validar
            if (!cep) { alert('❌ Digite o CEP de destino'); return; }
            if (!peso || peso <= 0) { alert('❌ Digite um peso válido'); return; }
            if (!valorNF || valorNF <= 0) { alert('❌ Digite um valor de NF válido'); return; }
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Calculando...';
            
            document.getElementById('resultadoDados').style.display = 'none';
            document.getElementById('erroArea').style.display = 'none';
            
            try {
                const formData = new URLSearchParams();
                formData.append('cep_destino', cep);
                formData.append('peso', peso);
                formData.append('valor_nf', valorNF);
                formData.append('modalidade', modalidade);
                formData.append('cliente_nome', 'Cliente Teste');
                formData.append('cliente_documento', '');
                
                const response = await fetch('/simulador/calcular', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const d = result.dados;
                    document.getElementById('numeroCotacao').textContent = d.numero_cotacao;
                    document.getElementById('resDestino').textContent = d.destino;
                    document.getElementById('resTipo').textContent = d.tipo;
                    document.getElementById('resPrazo').textContent = d.prazo;
                    document.getElementById('resPeso').textContent = d.peso;
                    document.getElementById('resModalidade').textContent = d.modalidade;
                    document.getElementById('resFrete').textContent = 'R$ ' + d.valor_base.toFixed(2);
                    document.getElementById('resSeguro').textContent = 'R$ ' + d.seguro.toFixed(2);
                    document.getElementById('resTotal').textContent = 'R$ ' + d.total.toFixed(2);
                    
                    document.getElementById('resultadoDados').style.display = 'block';
                } else {
                    const erro = document.getElementById('erroArea');
                    erro.style.display = 'block';
                    erro.textContent = '❌ ' + (result.message || 'Erro ao calcular frete');
                }
            } catch (error) {
                const erro = document.getElementById('erroArea');
                erro.style.display = 'block';
                erro.textContent = '❌ Erro ao conectar com o servidor. Tente novamente.';
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-calculator me-2"></i> Calcular Frete';
            }
        }

        function limparResultado() {
            document.getElementById('resultadoDados').style.display = 'none';
            document.getElementById('erroArea').style.display = 'none';
            document.getElementById('cepDestino').value = '';
            document.getElementById('peso').value = '';
            document.getElementById('valorNF').value = '';
        }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """


@router.post("/calcular")
async def calcular_frete(
    cep_destino: str = Form(...),
    peso: float = Form(...),
    modalidade: str = Form("PACKAGE"),
    valor_nf: float = Form(0.0),
    cliente_nome: str = Form("Cliente não informado"),
    cliente_documento: str = Form("")
):
    calculator = FreteCalculator()

    cep_limpo = re.sub(r'\D', '', cep_destino)
    if len(cep_limpo) != 8:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "CEP inválido. Digite 8 dígitos."}
        )

    if peso <= 0:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Peso deve ser maior que zero."}
        )

    resultado = calculator.calcular(cep_limpo, peso, modalidade, valor_nf)

    if "erro" in resultado:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": resultado["erro"]}
        )

    numero_cotacao = gerar_cotacao_id()
    d = resultado["dados"]

    return {
        "success": True,
        "dados": {
            "numero_cotacao": numero_cotacao,
            "destino": f"{d['cidade']}/{d['uf']}",
            "tipo": d["tipo_tarifa"],
            "prazo": f"{d['prazo']} dias úteis",
            "peso": f"{peso:.3f} kg",
            "modalidade": modalidade,
            "valor_base": d["preco_final"],  # CORRIGIDO: agora usa "preco_final"
            "seguro": d["ad_valorem"],
            "total": d["total"],
            "cliente_nome": cliente_nome,
            "cliente_documento": cliente_documento
        }
    }