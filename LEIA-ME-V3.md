# JADLOG BRÁS — MOTOR V3

## O que esta versão altera

Somente o motor de frete e, opcionalmente, textos visíveis do simulador.

A V3 NÃO substitui nem altera:
- app/routes/home.py
- app/static/manifest.json
- app/static/sw.js
- app/static/icons/*
- splash animada
- botão/fluxo de instalação PWA
- Supabase
- autenticação

## Fluxo do cálculo

1. CEP digitado -> CIDATEN.
2. CIDATEN retorna UF, cidade, prazo, Tipo Tarifa, FRAP e % Seguro.
3. Modalidade selecionada -> PACKAGE ou .COM.
4. Tipo Tarifa:
   - Capital: regra SP CAPITAL.
   - Capital 1/2/3: GLM da modalidade.
   - Interior 1/2/3: GLM da modalidade.
5. Peso:
   - GLM regional até 30 kg: menor coluna que comporte o peso.
   - GLM regional >30 kg: GLM 30 kg + KG ADICIONAL x quilos excedentes.
   - Capital <=30 kg: preço promocional final.
   - Capital >30 kg: cálculo por kg derivado dos pontos da aba SP CAPITAL.
6. Lucro:
   1=13; 5=26; 10=44; 20=80; 30=130;
   40=140; 50=150; ...; 100=200.
7. NF > 100: aplica o % Seguro da CIDATEN.
8. Total = preço comercial + ad valorem.

## Observação importante sobre "Capital" > 30 kg

A aba SP CAPITAL fornece GLM em 40, 50, ..., 100 kg, mas não mostra explicitamente
uma célula "KG ADICIONAL". A V3 calcula o adicional por kg pela diferença entre
50 kg e 40 kg / 10 e retrocede esse mesmo incremento para 31–39 kg.

Isso reproduz exatamente os pontos de 40/50/.../100 da planilha e permite peso X.
É a única parte da V3 que é uma inferência matemática a partir da planilha consolidada.
Deve ser validada com o cliente em 31–39 kg antes do deploy definitivo.

Para Capital 1/2/3 e Interior 1/2/3 não há inferência: o KG ADICIONAL vem
diretamente da GLM original.

## Auditoria interna

O retorno possui `dados["_auditoria"]`, com GLM, tabela, lucro, kg adicional,
classificação e percentual de seguro. A interface do cliente final não deve mostrar
esse bloco.

## Instalação segura

Na raiz do projeto:

1. Faça uma cópia/backup da pasta.
2. Copie `app/services/*` deste pacote para `app/services/`.
3. Copie `tests/test_motor_v3.py` para `tests/`.
4. Opcional: rode `python limpar_ui_v3.py` para remover dicas técnicas da UI.
5. Rode:

    pip install -r requirements-dev.txt
    python -m py_compile app\services\cep_service.py app\services\frete_calculator.py app\services\tarifas_capital_v3.py app\services\tarifas_glm_v3.py
    python -c "from app.main import app; print('APP OK -', len(app.routes), 'rotas')"
    python -m pytest -q tests\test_motor_v3.py

Não faça git add/push antes dos testes passarem.
