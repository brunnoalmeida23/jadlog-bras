# app/services/cep_service.py
import re
import json
import os


class CEPService:
    """Serviço para buscar informações de CEP"""

    def __init__(self):
        self.dados_cep = self._carregar_dados()

    def _carregar_dados(self):
        """Carrega a base de dados de CEPs"""
        dados = {
            # ===== CAPITAIS =====
            "01000000": {"cidade": "São Paulo", "uf": "SP", "tipo_tarifa": "CAPITAL", "prazo": 2},
            "02000000": {"cidade": "São Paulo", "uf": "SP", "tipo_tarifa": "CAPITAL", "prazo": 2},
            "03000000": {"cidade": "São Paulo", "uf": "SP", "tipo_tarifa": "CAPITAL", "prazo": 2},
            "04000000": {"cidade": "São Paulo", "uf": "SP", "tipo_tarifa": "CAPITAL", "prazo": 2},
            "05000000": {"cidade": "São Paulo", "uf": "SP", "tipo_tarifa": "CAPITAL", "prazo": 2},
            "06000000": {"cidade": "São Paulo", "uf": "SP", "tipo_tarifa": "CAPITAL", "prazo": 2},
            "20000000": {"cidade": "Rio de Janeiro", "uf": "RJ", "tipo_tarifa": "CAPITAL", "prazo": 3},
            "30000000": {"cidade": "Belo Horizonte", "uf": "MG", "tipo_tarifa": "CAPITAL", "prazo": 3},
            "40000000": {"cidade": "Salvador", "uf": "BA", "tipo_tarifa": "CAPITAL", "prazo": 4},
            "50000000": {"cidade": "Recife", "uf": "PE", "tipo_tarifa": "CAPITAL", "prazo": 4},
            "60000000": {"cidade": "Fortaleza", "uf": "CE", "tipo_tarifa": "CAPITAL", "prazo": 4},
            "70000000": {"cidade": "Brasília", "uf": "DF", "tipo_tarifa": "CAPITAL", "prazo": 3},
            "80000000": {"cidade": "Curitiba", "uf": "PR", "tipo_tarifa": "CAPITAL", "prazo": 3},
            "88000000": {"cidade": "Florianópolis", "uf": "SC", "tipo_tarifa": "CAPITAL", "prazo": 3},
            "90000000": {"cidade": "Porto Alegre", "uf": "RS", "tipo_tarifa": "CAPITAL", "prazo": 3},
            "29000000": {"cidade": "Vitória", "uf": "ES", "tipo_tarifa": "CAPITAL", "prazo": 3},
            "74000000": {"cidade": "Goiânia", "uf": "GO", "tipo_tarifa": "CAPITAL", "prazo": 3},
            "79000000": {"cidade": "Campo Grande", "uf": "MS", "tipo_tarifa": "CAPITAL", "prazo": 3},

            # ===== INTERIOR =====
            "69900000": {"cidade": "Rio Branco", "uf": "AC", "tipo_tarifa": "INTERIOR", "prazo": 17},
            "69945000": {"cidade": "Cruzeiro do Sul", "uf": "AC", "tipo_tarifa": "INTERIOR", "prazo": 38},
            "69000000": {"cidade": "Manaus", "uf": "AM", "tipo_tarifa": "INTERIOR", "prazo": 18},
            "68900000": {"cidade": "Macapá", "uf": "AP", "tipo_tarifa": "INTERIOR", "prazo": 17},
            "66000000": {"cidade": "Belém", "uf": "PA", "tipo_tarifa": "INTERIOR", "prazo": 16},
            "76800000": {"cidade": "Porto Velho", "uf": "RO", "tipo_tarifa": "INTERIOR", "prazo": 15},
            "69300000": {"cidade": "Boa Vista", "uf": "RR", "tipo_tarifa": "INTERIOR", "prazo": 19},
            "77000000": {"cidade": "Palmas", "uf": "TO", "tipo_tarifa": "INTERIOR", "prazo": 10},
            "78000000": {"cidade": "Cuiabá", "uf": "MT", "tipo_tarifa": "INTERIOR", "prazo": 9},
            "65000000": {"cidade": "São Luís", "uf": "MA", "tipo_tarifa": "INTERIOR", "prazo": 15},
            "64000000": {"cidade": "Teresina", "uf": "PI", "tipo_tarifa": "INTERIOR", "prazo": 15},
            "58000000": {"cidade": "João Pessoa", "uf": "PB", "tipo_tarifa": "INTERIOR", "prazo": 16},
            "59000000": {"cidade": "Natal", "uf": "RN", "tipo_tarifa": "INTERIOR", "prazo": 11},
            "49000000": {"cidade": "Aracaju", "uf": "SE", "tipo_tarifa": "INTERIOR", "prazo": 10},
            "57000000": {"cidade": "Maceió", "uf": "AL", "tipo_tarifa": "INTERIOR", "prazo": 12},
        }

        # Carregar CEPs extras se existir
        cep_file = "ceps.json"
        if os.path.exists(cep_file):
            try:
                with open(cep_file, "r") as f:
                    dados_extra = json.load(f)
                    dados.update(dados_extra)
            except:
                pass

        return dados

    def buscar(self, cep: str) -> dict:
        """Busca informações de um CEP"""
        cep_limpo = re.sub(r'\D', '', cep)

        if cep_limpo in self.dados_cep:
            return self.dados_cep[cep_limpo]

        # Buscar por prefixo
        prefixo = cep_limpo[:5]
        for key, value in self.dados_cep.items():
            if key.startswith(prefixo):
                return value

        # Buscar por UF (fallback)
        uf = self._identificar_uf(cep_limpo)
        if uf:
            return {
                "cidade": "Não identificada",
                "uf": uf,
                "tipo_tarifa": "CAPITAL",
                "prazo": 5
            }

        return None

    def _identificar_uf(self, cep: str) -> str:
        """Identifica a UF pelo CEP"""
        uf_por_prefixo = {
            '01': 'SP', '02': 'SP', '03': 'SP', '04': 'SP', '05': 'SP',
            '06': 'SP', '07': 'SP', '08': 'SP', '09': 'SP',
            '10': 'SP', '11': 'SP', '12': 'SP', '13': 'SP', '14': 'SP',
            '15': 'SP', '16': 'SP', '17': 'SP', '18': 'SP', '19': 'SP',
            '20': 'RJ', '21': 'RJ', '22': 'RJ', '23': 'RJ', '24': 'RJ',
            '25': 'RJ', '26': 'RJ', '27': 'RJ', '28': 'RJ', '29': 'ES',
            '30': 'MG', '31': 'MG', '32': 'MG', '33': 'MG', '34': 'MG',
            '35': 'MG', '36': 'MG', '37': 'MG', '38': 'MG', '39': 'MG',
            '40': 'BA', '41': 'BA', '42': 'BA', '43': 'BA', '44': 'BA',
            '45': 'BA', '46': 'BA', '47': 'BA', '48': 'BA', '49': 'SE',
            '50': 'PE', '51': 'PE', '52': 'PE', '53': 'PE', '54': 'PE',
            '55': 'PE', '56': 'PE', '57': 'AL', '58': 'PB', '59': 'RN',
            '60': 'CE', '61': 'CE', '62': 'CE', '63': 'CE', '64': 'PI',
            '65': 'MA', '66': 'PA', '67': 'PA', '68': 'PA', '69': 'AC',
            '70': 'DF', '71': 'DF', '72': 'DF', '73': 'DF', '74': 'GO',
            '75': 'GO', '76': 'GO', '77': 'TO', '78': 'MT', '79': 'MS',
            '80': 'PR', '81': 'PR', '82': 'PR', '83': 'PR', '84': 'PR',
            '85': 'PR', '86': 'PR', '87': 'PR', '88': 'SC', '89': 'SC',
            '90': 'RS', '91': 'RS', '92': 'RS', '93': 'RS', '94': 'RS',
            '95': 'RS', '96': 'RS', '97': 'RS', '98': 'RS', '99': 'RS'
        }
        prefixo = cep[:2]
        return uf_por_prefixo.get(prefixo, 'SP')