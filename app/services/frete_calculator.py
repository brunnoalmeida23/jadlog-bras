from .cep_service import CEPService

class FreteCalculator:
    def __init__(self):
        self.cep_service = CEPService()
    
    def calcular(self, cep: str, peso: float, modalidade: str = "PACKAGE", valor_nf: float = 0.0):
        info_cep = self.cep_service.buscar(cep)
        if not info_cep:
            return {"erro": "CEP não encontrado"}
        
        tipo_tarifa = info_cep.get("tipo_tarifa", "CAPITAL")
        subtotal = self._calcular_frete_base(peso, modalidade, tipo_tarifa)
        ad_valorem = self._calcular_seguro(valor_nf)
        total = subtotal + ad_valorem
        
        return {
            "subtotal": subtotal,
            "ad_valorem": ad_valorem,
            "total": total,
            "tipo_tarifa": tipo_tarifa
        }
    
    def _calcular_frete_base(self, peso: float, modalidade: str, tipo_tarifa: str) -> float:
        tabela_capital = {
            ("PACKAGE", 1): 24.99, ("PACKAGE", 5): 49.99,
            ("PACKAGE", 10): 79.99, ("PACKAGE", 20): 149.99,
            ("PACKAGE", 30): 229.99,
            (".COM", 1): 19.99, (".COM", 5): 39.99,
            (".COM", 10): 59.99, (".COM", 20): 99.99,
            (".COM", 30): 159.99,
        }
        
        multiplicador = 1.3 if tipo_tarifa == "INTERIOR" else 1.0
        faixas = sorted([k[1] for k in tabela_capital.keys() if k[0] == modalidade])
        peso_limite = None
        
        for faixa in faixas:
            if peso <= faixa:
                peso_limite = faixa
                break
        
        if peso_limite is None:
            peso_limite = faixas[-1] if faixas else 30
        
        chave = (modalidade, peso_limite)
        if chave in tabela_capital:
            valor = tabela_capital[chave] * multiplicador
        else:
            base = tabela_capital.get((modalidade, 30), 229.99) * multiplicador
            valor = base * (peso / 30)
        
        return round(valor, 2)
    
    def _calcular_seguro(self, valor_nf: float) -> float:
        if valor_nf <= 0:
            return 0.0
        return round(valor_nf * 0.0066, 2)
