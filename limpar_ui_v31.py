"""
Patch VISUAL opcional da V3.1.

Remove somente informações internas do recibo/tela do cliente:
- Tipo/classificação tarifária;
- Seguro como linha separada (o total continua correto no backend);
- textos técnicos GLM/ad valorem/lucro.

Não altera home.py, manifest.json, sw.js, ícones, splash ou instalação PWA.
Cria backup antes de alterar simulador.py.
"""
from pathlib import Path
from datetime import datetime
import re
import shutil

arquivo = Path("app/routes/simulador.py")
if not arquivo.exists():
    raise SystemExit("ERRO: app/routes/simulador.py não encontrado.")

texto = arquivo.read_text(encoding="utf-8-sig")
original = texto

backup = arquivo.with_name(
    f"simulador.py.backup-v31-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
)
shutil.copy2(arquivo, backup)

# Remove itens internos do array de detalhes do recibo.
for rotulo in ("Tipo", "Seguro"):
    texto = re.sub(
        rf'(?m)^[ \t]*\[\s*[\'"]{rotulo}[\'"]\s*,\s*[^\n]+\],?\s*\n',
        "",
        texto,
    )

# Remove pequenos textos técnicos restantes.
texto = re.sub(
    r'(?im)^[ \t]*<small[^>]*>[^<]*(?:GLM|ad\s*valorem|lucro|seguro\s*:)[^<]*</small>[ \t]*\r?\n?',
    "",
    texto,
)

if texto != original:
    arquivo.write_text(texto, encoding="utf-8")
    print("UI V3.1 limpa com sucesso.")
else:
    print("Nenhum item visual conhecido precisava ser alterado.")

print("Backup:", backup)
print("PWA/splash NÃO foram alterados.")
