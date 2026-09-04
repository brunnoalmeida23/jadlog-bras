# limpar_ui_v3.py
"""
Patch conservador de textos do simulador.

- Faz backup de app/routes/simulador.py.
- Remove apenas dicas comerciais/técnicas visíveis ao cliente final.
- Não toca em home.py, manifest.json, sw.js, ícones ou configuração PWA.
"""
from pathlib import Path
import re
import shutil
from datetime import datetime

arquivo = Path("app/routes/simulador.py")
if not arquivo.exists():
    raise SystemExit("ERRO: app/routes/simulador.py não encontrado. Execute na raiz do projeto.")

texto = arquivo.read_text(encoding="utf-8-sig")
original = texto

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = arquivo.with_name(f"simulador.py.backup-v3-{timestamp}")
shutil.copy2(arquivo, backup)

substituicoes = [
    ('placeholder="Ex: 2.350"', 'placeholder="Digite o peso desejado"'),
    ("placeholder='Ex: 2.350'", "placeholder='Digite o peso desejado'"),
    ('placeholder="Ex: 5000.00"', 'placeholder="Digite o valor da nota fiscal"'),
    ("placeholder='Ex: 5000.00'", "placeholder='Digite o valor da nota fiscal'"),
    ('placeholder="Ex: 01000-000"', 'placeholder="Digite o CEP de destino"'),
    ("placeholder='Ex: 01000-000'", "placeholder='Digite o CEP de destino'"),
]
for antigo, novo in substituicoes:
    texto = texto.replace(antigo, novo)

# Remove pequenos textos de ajuda que revelam regra interna ou exemplos desnecessários.
texto = re.sub(
    r'(?im)^[ \t]*<small[^>]*>[^<]*(?:Ex:\s*2\.350|Ex:\s*01000-000|Seguro:|ad\s*valorem|GLM)[^<]*</small>[ \t]*\r?\n?',
    '',
    texto,
)

# Remove linha "Seguro" do detalhamento do recibo, se essa versão da UI ainda a tiver.
texto = re.sub(
    r'(?m)^[ \t]*\[\s*[\'"]Seguro[\'"]\s*,\s*[^\n]+\],?\s*\n',
    '',
    texto,
)

# Remove observações textuais de composição do tipo GLM + lucro + seguro.
texto = re.sub(
    r'(?im)^[ \t]*<[^>]+>[^<]*(?:GLM\s*\+|ad\s*valorem)[^<]*</[^>]+>[ \t]*\r?\n?',
    '',
    texto,
)

if texto == original:
    print("Nenhum texto conhecido precisava ser alterado. Backup criado em:", backup)
else:
    arquivo.write_text(texto, encoding="utf-8")
    print("UI limpa com sucesso.")
    print("Backup:", backup)

print("PWA NÃO foi alterado por este script.")
