# JadLog Brás — Motor de Homologação V3.1

## Fonte de verdade

A V3.1 usa a seguinte hierarquia:

1. `Cidaten_2026.xlsx`
   - identifica o CEP por faixa;
   - retorna UF, cidade, prazo, classificação tarifária e percentual de seguro.

2. `PLANILHA-CAP-INT.xlsx`
   - é a consolidação operacional do projeto;
   - aba `SP CAPITAL`: regra especial para destinos classificados literalmente como `Capital`;
   - abas `INTERIOR - CAP (1-2-3) - PACK` e `.COM`: âncoras de validação para Capital 1/2/3 e Interior 1/2/3.

3. `GLM Pack e .Com LIEV.xlsx`
   - fornece a granularidade completa de peso até 30 kg e o `Kg Adicional`;
   - as âncoras 1/5/10/20/30 + adicional foram confrontadas contra a CAP x INT.

4. Lucro comercial confirmado
   - até 1 kg: 13
   - até 5 kg: 26
   - até 10 kg: 44
   - até 20 kg: 80
   - até 30 kg: 130
   - 31–40: 140
   - 41–50: 150
   - 51–60: 160
   - 61–70: 170
   - 71–80: 180
   - 81–90: 190
   - 91–100: 200

O `painel.vocequemanda.com` NÃO é fonte de cálculo desta versão.

## Regras

### Classificação `Capital`
Até 30 kg usa os preços fixos da aba `SP CAPITAL`:
1 = 24,99; 5 = 49,99; 10 = 79,99; 20 = 149,99; 30 = 229,99.

Acima de 30 kg usa os pontos GLM da mesma aba (40/50/.../100 kg) e calcula
pesos intermediários por incremento por kg entre os pontos consecutivos.
Depois soma o lucro da faixa.

### Capital 1/2/3 e Interior 1/2/3
A modalidade selecionada define a tabela:
- PACKAGE -> GLM pack
- .COM -> GLM com

Até 30 kg o motor usa a coluna GLM que comporta o peso.
Acima de 30 kg:
`GLM(30 kg) + kg excedente tarifável × Kg Adicional`.
Depois soma o lucro da faixa.

### Seguro / ad valorem
Se `valor_nf > 100`, o percentual utilizado vem da linha encontrada na CIDATEN.
O detalhamento fica em `_auditoria` e não deve ser exibido ao cliente.

## PWA

Este pacote NÃO contém nem altera:
- `app/routes/home.py`
- `manifest.json`
- `sw.js`
- ícones PWA
- splash/loading screen

Portanto, copiar os arquivos do motor não remove a instalação PWA ou a splash.

## Instalação

Na raiz do projeto, substitua/adicione apenas:

- `app/services/cep_service.py`
- `app/services/frete_calculator.py`
- `app/services/tarifas_capital_v31.py`
- `app/services/tarifas_glm_v31.py`
- `tests/`
- `validar_cotacao_v31.py`

`limpar_ui_v31.py` é opcional e mexe SOMENTE em `app/routes/simulador.py`.

## Testes

```powershell
python -m py_compile app\services\cep_service.py app\services\frete_calculator.py app\services\tarifas_capital_v31.py app\services\tarifas_glm_v31.py
python -c "from app.main import app; print('APP OK -', len(app.routes), 'rotas')"
python -m pytest -q tests\test_motor_v31.py
```

A suíte V3.1 inclui uma conferência de 1.944 pontos entre CAP x INT e GLM LIEV.

## Teste manual

```powershell
python validar_cotacao_v31.py 03309000 10 PACKAGE 100
python validar_cotacao_v31.py 03309000 35 PACKAGE 100
```

Não faça `git push` antes da homologação manual.
