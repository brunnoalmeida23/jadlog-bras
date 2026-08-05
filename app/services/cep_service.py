import pandas as pd
import bisect
import re
from typing import Optional, Dict, Tuple

class CEPService:
    def __init__(self, arquivo_cidaten: str = "Cidaten_2026.xlsx"):
        self.arquivo = arquivo_cidaten
        self.dados = []  # (inicio, fim, uf, localidade, tipo_tarifa, prazo, seguro)
        self.inicios = []
        self._carregar()

    def _parse_intervalo(self, cep_str: str) -> Tuple[int, int]:
        """Converte string de CEP para (inicio, fim) como inteiros."""
        cep_str = cep_str.strip()
        if ' a ' in cep_str:
            partes = cep_str.split(' a ')
            inicio = int(partes[0].strip())
            fim = int(partes[1].strip())
        else:
            # Caso único
            inicio = int(cep_str)
            fim = inicio
        return inicio, fim

    def _carregar(self):
        try:
            df = pd.read_excel(self.arquivo, sheet_name="Cidaten", header=1)
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar CIDATEN: {e}")

        # Mapeamento de colunas - ajuste se necessário
        # As colunas são: UF, Localidade, Cep, Prazo Rodo, Tipo Tarifa, Frap (Fob), % Seguro
        # Vamos usar índices ou nomes exatos
        # A planilha tem cabeçalho: UF | Localidade | Cep | Prazo Rodo | Tipo Tarifa | Frap (Fob) | % Seguro
        # Portanto, vamos acessar por posição ou nome

        # Para garantir, vamos usar os nomes das colunas conforme aparecem
        col_uf = 'UF'
        col_localidade = 'Localidade'
        col_cep = 'Cep'
        col_prazo = 'Prazo Rodo'
        col_tipo = 'Tipo Tarifa'
        col_seguro = '% Seguro'

        for idx, row in df.iterrows():
            uf = str(row[col_uf]).strip()
            localidade = str(row[col_localidade]).strip()
            cep_str = str(row[col_cep]).strip()
            prazo = int(row[col_prazo]) if pd.notna(row[col_prazo]) else 0
            tipo = str(row[col_tipo]).strip()
            seguro = float(row[col_seguro]) if pd.notna(row[col_seguro]) else 0.0066

            inicio, fim = self._parse_intervalo(cep_str)
            self.dados.append((inicio, fim, uf, localidade, tipo, prazo, seguro))

        # Ordenar por início
        self.dados.sort(key=lambda x: x[0])
        self.inicios = [item[0] for item in self.dados]  # lista de inteiros

    def buscar(self, cep):
        """
        Busca informações do CEP.
        cep pode ser string (com ou sem hífen) ou inteiro.
        Retorna dicionário ou None.
        """
        # Normalizar CEP para inteiro
        if isinstance(cep, str):
            cep_clean = re.sub(r'\D', '', cep)  # remove tudo que não é dígito
            try:
                cep_int = int(cep_clean)
            except ValueError:
                return None
        else:
            cep_int = int(cep)

        # Busca binária
        pos = bisect.bisect_right(self.inicios, cep_int) - 1
        if pos < 0:
            return None

        inicio, fim, uf, localidade, tipo_tarifa, prazo, seguro = self.dados[pos]
        if cep_int < inicio or cep_int > fim:
            # Verifica próximo
            if pos + 1 < len(self.dados):
                inicio2, fim2, uf2, localidade2, tipo_tarifa2, prazo2, seguro2 = self.dados[pos+1]
                if inicio2 <= cep_int <= fim2:
                    inicio, fim, uf, localidade, tipo_tarifa, prazo, seguro = self.dados[pos+1]
                else:
                    return None
            else:
                return None

        # Extrair regiao_interior se for Interior
        regiao_interior = None
        if "Interior" in tipo_tarifa:
            match = re.search(r'\d+', tipo_tarifa)
            if match:
                regiao_interior = f"INT{match.group()}"
            else:
                regiao_interior = "INT1"

        return {
            "uf": uf,
            "cidade": localidade,
            "tipo_tarifa": tipo_tarifa,
            "regiao_interior": regiao_interior,
            "prazo": prazo,
            "seguro_percentual": seguro,
        }