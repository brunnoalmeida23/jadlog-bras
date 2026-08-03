from __future__ import annotations

import json
import os
import re
import unicodedata
from typing import Any


class ClienteService:
    """Cadastro e pesquisa de clientes em armazenamento local."""

    def __init__(self) -> None:
        raiz_projeto = os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))
        )

        self.arquivo_clientes = os.path.join(
            raiz_projeto,
            "clientes.json",
        )

        self.clientes = self._carregar_clientes()

    @staticmethod
    def _somente_numeros(valor: str) -> str:
        return re.sub(r"\D", "", str(valor or ""))

    @staticmethod
    def _normalizar_texto(valor: str) -> str:
        texto = str(valor or "").strip().lower()

        texto = unicodedata.normalize("NFKD", texto)

        return "".join(
            caractere
            for caractere in texto
            if not unicodedata.combining(caractere)
        )

    def _carregar_clientes(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.arquivo_clientes):
            return []

        try:
            with open(
                self.arquivo_clientes,
                "r",
                encoding="utf-8",
            ) as arquivo:
                dados = json.load(arquivo)

            if isinstance(dados, list):
                return dados

        except (OSError, json.JSONDecodeError):
            pass

        return []

    def _salvar_clientes(self) -> None:
        with open(
            self.arquivo_clientes,
            "w",
            encoding="utf-8",
        ) as arquivo:
            json.dump(
                self.clientes,
                arquivo,
                ensure_ascii=False,
                indent=2,
            )

    def buscar(self, termo: str) -> dict[str, Any]:
        termo_original = str(termo or "").strip()

        if not termo_original:
            return {
                "success": False,
                "dados": [],
                "message": "Digite CPF, CNPJ, nome ou razão social.",
            }

        termo_numerico = self._somente_numeros(termo_original)
        termo_texto = self._normalizar_texto(termo_original)

        resultados: list[dict[str, Any]] = []

        for cliente in self.clientes:
            documento = self._somente_numeros(
                cliente.get("cpf_cnpj", "")
            )

            nome = self._normalizar_texto(
                cliente.get("nome", "")
            )

            razao_social = self._normalizar_texto(
                cliente.get("razao_social", "")
            )

            documento_encontrado = (
                bool(termo_numerico)
                and termo_numerico == documento
            )

            nome_encontrado = (
                bool(termo_texto)
                and (
                    termo_texto in nome
                    or termo_texto in razao_social
                )
            )

            if documento_encontrado or nome_encontrado:
                resultados.append(cliente)

        if not resultados:
            return {
                "success": False,
                "dados": [],
                "message": "Cliente não encontrado.",
            }

        return {
            "success": True,
            "dados": resultados,
            "quantidade": len(resultados),
            "message": "Cliente encontrado.",
        }

    def salvar_cliente(
        self,
        cpf_cnpj: str,
        nome: str,
        razao_social: str = "",
        endereco: str = "",
        cidade: str = "",
        uf: str = "",
        cep: str = "",
        telefone: str = "",
    ) -> dict[str, Any]:

        documento = self._somente_numeros(cpf_cnpj)
        nome_limpo = str(nome or "").strip()
        razao_limpa = str(razao_social or "").strip()

        if len(documento) not in (11, 14):
            return {
                "success": False,
                "message": "Informe um CPF ou CNPJ válido.",
            }

        if not nome_limpo and not razao_limpa:
            return {
                "success": False,
                "message": (
                    "Informe o nome completo ou a razão social."
                ),
            }

        for cliente in self.clientes:
            documento_existente = self._somente_numeros(
                cliente.get("cpf_cnpj", "")
            )

            if documento_existente == documento:
                return {
                    "success": False,
                    "message": "CPF ou CNPJ já cadastrado.",
                }

        novo_cliente = {
            "id": len(self.clientes) + 1,
            "cpf_cnpj": documento,
            "nome": nome_limpo,
            "razao_social": razao_limpa,
            "endereco": str(endereco or "").strip(),
            "cidade": str(cidade or "").strip(),
            "uf": str(uf or "").strip().upper(),
            "cep": self._somente_numeros(cep),
            "telefone": str(telefone or "").strip(),
        }

        self.clientes.append(novo_cliente)
        self._salvar_clientes()

        return {
            "success": True,
            "dados": novo_cliente,
            "message": "Cliente cadastrado com sucesso.",
        }