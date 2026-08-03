from datetime import datetime
import re
import random

def gerar_cotacao_id() -> str:
    ano = datetime.now().year
    seq = random.randint(1, 9999)
    return f"COT-{ano}-{seq:04d}"

def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:.2f}".replace(".", ",")

def formatar_cep(cep: str) -> str:
    cep_limpo = re.sub(r'\D', '', cep)
    if len(cep_limpo) == 8:
        return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
    return cep
