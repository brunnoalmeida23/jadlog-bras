# app/utils/helpers.py
from datetime import datetime
import re
import random


def gerar_cotacao_id() -> str:
    """Gera um número único para cotação"""
    ano = datetime.now().year
    seq = random.randint(1, 9999)
    return f"COT-{ano}-{seq:04d}"


def formatar_moeda(valor: float) -> str:
    """Formata um valor para moeda brasileira"""
    return f"R$ {valor:.2f}".replace(".", ",")


def formatar_cep(cep: str) -> str:
    """Formata um CEP para exibição"""
    cep_limpo = re.sub(r'\D', '', cep)
    if len(cep_limpo) == 8:
        return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
    return cep


def calcular_prazo(uf: str, tipo_tarifa: str) -> int:
    """Calcula o prazo baseado na UF e tipo de tarifa"""
    prazos = {
        "SP": {"CAPITAL": 2, "INTERIOR": 3},
        "RJ": {"CAPITAL": 3, "INTERIOR": 4},
        "MG": {"CAPITAL": 3, "INTERIOR": 4},
        "PR": {"CAPITAL": 3, "INTERIOR": 4},
        "SC": {"CAPITAL": 3, "INTERIOR": 4},
        "RS": {"CAPITAL": 3, "INTERIOR": 4},
        "BA": {"CAPITAL": 4, "INTERIOR": 5},
        "DF": {"CAPITAL": 3, "INTERIOR": 4},
        "GO": {"CAPITAL": 3, "INTERIOR": 4},
        "MS": {"CAPITAL": 3, "INTERIOR": 4},
        "ES": {"CAPITAL": 3, "INTERIOR": 4},
        "AC": {"CAPITAL": 17, "INTERIOR": 38},
        "AM": {"CAPITAL": 18, "INTERIOR": 25},
        "AP": {"CAPITAL": 17, "INTERIOR": 27},
        "PA": {"CAPITAL": 16, "INTERIOR": 20},
        "RO": {"CAPITAL": 15, "INTERIOR": 26},
        "RR": {"CAPITAL": 19, "INTERIOR": 40},
        "TO": {"CAPITAL": 10, "INTERIOR": 20},
        "MT": {"CAPITAL": 9, "INTERIOR": 15},
        "MA": {"CAPITAL": 15, "INTERIOR": 22},
        "PI": {"CAPITAL": 15, "INTERIOR": 23},
        "PB": {"CAPITAL": 16, "INTERIOR": 22},
        "RN": {"CAPITAL": 11, "INTERIOR": 18},
        "SE": {"CAPITAL": 10, "INTERIOR": 16},
        "AL": {"CAPITAL": 12, "INTERIOR": 16},
        "CE": {"CAPITAL": 4, "INTERIOR": 5},
        "PE": {"CAPITAL": 4, "INTERIOR": 5},
    }
    
    return prazos.get(uf, {}).get(tipo_tarifa, 5)