# JadLog Brás — Motor V3.2

## O que mudou em relação à V3.1

A V3.1 interpolava matematicamente os valores da aba **SP CAPITAL** entre 40/50/.../100 kg. Isso não era sustentado pela planilha, porque essa aba não possui coluna `KG ADICIONAL`.

A V3.2 remove essa inferência. Para classificação CIDATEN literal `Capital`:

- até 30 kg: preços promocionais fixos da aba SP CAPITAL;
- 31 a 40 kg: usa o GLM da coluna 40 kg + lucro da faixa 40;
- 41 a 50 kg: usa o GLM da coluna 50 kg + lucro da faixa 50;
- e assim por diante até 100 kg.

A aba SP CAPITAL também **não separa PACKAGE de .COM**. Por isso a V3.2 não inventa uma diferença entre modalidades nessa classificação específica. A modalidade continua registrada na cotação, mas o valor da regra `Capital` é o mesmo.

Para `Capital 1/2/3` e `Interior 1/2/3`, permanece a regra da GLM LIEV / CAP X INT:

- PACKAGE e .COM usam tabelas distintas;
- até 30 kg usa o peso GLM correspondente;
- acima de 30 kg usa `GLM 30 kg + kg excedente × KG ADICIONAL`;
- depois soma o lucro da faixa e o ad valorem quando aplicável.

## Segurança do PWA

Este pacote não contém `home.py`, `manifest.json`, `sw.js` nem ícones. Portanto não altera instalação PWA, splash ou tela de carregamento.

## Instalação

Copie os arquivos preservando as pastas e rode:

```powershell
python -m py_compile app\services\cep_service.py app\services\frete_calculator.py app\services\tarifas_capital_v32.py app\services\tarifas_glm_v32.py
python -c "from app.main import app; print('APP OK -', len(app.routes), 'rotas')"
python -m pytest -q tests\test_motor_v32.py
```

Depois, teste:

```powershell
python validar_cotacao_v32.py 03309000 35 PACKAGE 100
python validar_cotacao_v32.py 03309000 35 .COM 100
```

Resultado esperado para SP / Capital / 35 kg / NF 100 conforme CAP X INT corrigida:

- GLM faixa 40 kg: R$ 105,18
- lucro faixa 40 kg: R$ 140,00
- frete: R$ 245,18
- seguro: R$ 0,00
- total: R$ 245,18

Não faça commit/push antes da homologação manual.
