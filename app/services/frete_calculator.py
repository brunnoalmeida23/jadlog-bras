# app/services/frete_calculator.py
from .tabela_frete import TABELA_FRETE
import bisect

class FreteCalculator:
    def __init__(self):
        # Usar a nova tabela extraída da planilha
        self.tabela = TABELA_FRETE
        self.lucro = self._carregar_lucro()

    def _carregar_lucro(self):
        """LUCRO do revendedor (tabela de pesagem)"""
        return {
            1: 13.00, 5: 26.00, 10: 44.00, 20: 80.00, 30: 130.00,
            40: 140.00, 50: 150.00, 60: 160.00, 70: 170.00,
            80: 180.00, 90: 190.00, 100: 200.00
        }

    def _obter_glm(self, uf: str, tipo_tarifa: str, peso: float) -> float:
        """Obtém o GLM da tabela para a UF, tipo de tarifa e peso"""
        # Capital 1, 2, 3 - usar o primeiro que encontrar
        tipo_base = tipo_tarifa.split()[0]  # "Capital" ou "Interior"
        
        # Procurar pela chave exata
        chave = f"{uf}_{tipo_tarifa}"
        if chave in self.tabela:
            dados = self.tabela[chave]
        else:
            # Se não encontrar, tentar com "Capital 1" ou "Interior 1"
            chave_fallback = f"{uf}_{tipo_base} 1"
            if chave_fallback in self.tabela:
                dados = self.tabela[chave_fallback]
            else:
                # Fallback para SP Capital 1
                dados = self.tabela.get("SP_Capital 1", {})
                if not dados:
                    return 0
        
        pesos = dados.get("pesos", {})
        kg_adicional = dados.get("kg_adicional", 0)
        
        # Buscar o valor para o peso
        # Se o peso for <= 0.25, usar 0.25
        if peso <= 0.25:
            return pesos.get(0.25, 0)
        
        # Para pesos > 30, usar kg_adicional
        if peso > 30:
            valor_30 = pesos.get(30, 0)
            excesso = peso - 30
            return valor_30 + (excesso * kg_adicional)
        
        # Interpolação linear entre os pesos disponíveis
        pesos_ordenados = sorted(pesos.keys())
        
        # Se o peso exceder o maior, usa kg_adicional
        if peso > pesos_ordenados[-1]:
            ultimo_peso = pesos_ordenados[-1]
            ultimo_valor = pesos[ultimo_peso]
            if kg_adicional > 0:
                return ultimo_valor + (peso - ultimo_peso) * kg_adicional
            return ultimo_valor
        
        # Encontrar o intervalo
        for i in range(len(pesos_ordenados) - 1):
            p1 = pesos_ordenados[i]
            p2 = pesos_ordenados[i + 1]
            if p1 <= peso <= p2:
                v1 = pesos[p1]
                v2 = pesos[p2]
                if p2 == p1:
                    return v1
                return v1 + (v2 - v1) * (peso - p1) / (p2 - p1)
        
        return pesos.get(peso, 0)

    def _obter_lucro(self, peso: float) -> float:
        """Obtém o lucro baseado no peso"""
        if peso <= 1:
            return self.lucro[1]
        elif peso <= 5:
            return self.lucro[5]
        elif peso <= 10:
            return self.lucro[10]
        elif peso <= 20:
            return self.lucro[20]
        elif peso <= 30:
            return self.lucro[30]
        elif peso <= 40:
            return self.lucro[40]
        elif peso <= 50:
            return self.lucro[50]
        elif peso <= 60:
            return self.lucro[60]
        elif peso <= 70:
            return self.lucro[70]
        elif peso <= 80:
            return self.lucro[80]
        elif peso <= 90:
            return self.lucro[90]
        else:
            return self.lucro[100]

    def calcular(self, cep: str, peso: float, modalidade: str = "PACKAGE", valor_nf: float = 0.0) -> dict:
        """Calcula o frete baseado no CEP, peso, modalidade e valor da NF"""
        from .cep_service import CEPService
        
        cep_service = CEPService()
        info_cep = cep_service.buscar(cep)
        
        if not info_cep:
            return {"erro": f"CEP {cep} não encontrado"}

        uf = info_cep.get("uf", "SP")
        tipo_tarifa = info_cep.get("tipo_tarifa", "Capital")
        cidade = info_cep.get("cidade", "")
        prazo = info_cep.get("prazo", 5)
        seguro_percentual = info_cep.get("seguro_percentual", 0.0066)
        regiao_interior = info_cep.get("regiao_interior")  # "INT1", "INT2", "INT3" ou None

        # GLM - usar a nova tabela
        glm = self._obter_glm(uf, tipo_tarifa, peso)
        
        # LUCRO
        lucro = self._obter_lucro(peso)
        
        preco_final = glm + lucro
        
        # Seguro (Ad Valorem)
        seguro = 0
        if valor_nf > 100:
            seguro = round(valor_nf * seguro_percentual, 2)
        
        total = round(preco_final + seguro, 2)

        return {
            "success": True,
            "dados": {
                "cep": cep,
                "uf": uf,
                "cidade": cidade,
                "tipo_tarifa": tipo_tarifa,
                "regiao_interior": regiao_interior if "Interior" in tipo_tarifa else None,
                "prazo": prazo,
                "peso": peso,
                "modalidade": modalidade,
                "glm": round(glm, 2),
                "lucro": round(lucro, 2),
                "preco_final": round(preco_final, 2),
                "seguro": seguro,
                "total": total,
                "valor_nf": valor_nf
            }
        }