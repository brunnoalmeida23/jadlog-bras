# app/services/sessao.py
"""Gerenciamento de sessões para autenticação"""

# Dicionário de sessões (em produção, use Redis ou banco de dados)
sessoes = {}


def verificar_sessao(token: str) -> bool:
    """Verifica se um token é válido"""
    return token and token in sessoes


def adicionar_sessao(token: str):
    """Adiciona um token à sessão"""
    sessoes[token] = True


def remover_sessao(token: str):
    """Remove um token da sessão"""
    if token in sessoes:
        del sessoes[token]