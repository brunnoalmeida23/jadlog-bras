# app/services/frete_calculator.py
import bisect
from .tabela_dropf import TABELA_DROPF
from .tabela_frete import TABELA_FRETE
from .cep_service import CEPService

class FreteCalculator:
    def __init__(self):
        self.tabela = TABELA_FRETE
        self.tabela_dropf = TABELA_DROPF
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
        tipo_base = tipo_tarifa.split()[0]
        
        chave = f"{uf}_{tipo_tarifa}"
        if chave in self.tabela:
            dados = self.tabela[chave]
        else:
            chave_fallback = f"{uf}_{tipo_base} 1"
            dados = self.tabela.get(chave_fallback, self.tabela.get("SP_Capital 1", {}))
            if not dados:
                return 0.0
        
        pesos = dados.get("pesos", {})
        kg_adicional = dados.get("kg_adicional", 0.0)
        
        if peso <= 0.25:
            return pesos.get(0.25, 0.0)
        
        if peso > 30:
            valor_30 = pesos.get(30, 0.0)
            return valor_30 + ((peso - 30) * kg_adicional)
        
        pesos_ordenados = sorted(pesos.keys())
        
        if peso > pesos_ordenados[-1]:
            ultimo_peso = pesos_ordenados[-1]
            return pesos[ultimo_peso] + ((peso - ultimo_peso) * kg_adicional if kg_adicional > 0 else 0)
        
        # Usando bisect para encontrar o intervalo de forma eficiente
        idx = bisect.bisect_left(pesos_ordenados, peso)
        if idx == 0:
            return pesos[pesos_ordenados[0]]
        
        p1 = pesos_ordenados[idx - 1]
        p2 = pesos_ordenados[idx]
        v1 = pesos[p1]
        v2 = pesos[p2]
        
        if p1 == p2:
            return v1
            
        return v1 + (v2 - v1) * (peso - p1) / (p2 - p1)

    def _obter_glm_dropf(self, uf: str, peso: float) -> float:
        """Obtém o GLM da tabela DROPF para a UF e peso"""
        limites = [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]
        
        for key, dados in self.tabela_dropf.items():
            if key.startswith(uf):
                pesos = dados.get("pesos", {})
                for limite in limites:
                    if peso <= limite:
                        return pesos.get(limite, 0.0)
                return pesos.get(100, 0.0)
        
        # Fallback para SP
        dados_sp = self.tabela_dropf.get("SP_4474970", {})
        pesos_sp = dados_sp.get("pesos", {})
        if peso <= 10:
            return pesos_sp.get(10, 86.05)
        elif peso <= 30:
            return pesos_sp.get(30, 222.92)
        return pesos_sp.get(100, 725.68)

    def _obter_lucro(self, peso: float) -> float:
        """Obtém o lucro baseado no peso de forma dinâmica"""
        chaves_lucro = sorted(self.lucro.keys())
        idx = bisect.bisect_left(chaves_lucro, peso)
        
        if idx >= len(chaves_lucro):
            return self.lucro[chaves_lucro[-1]]
        
        return self.lucro[chaves_lucro[idx]]

    def calcular(self, cep: str, peso: float, modalidade: str = "PACKAGE", valor_nf: float = 0.0) -> dict:
        """Calcula o frete baseado no CEP, peso, modalidade e valor da NF"""
        cep_service = CEPService()
        info_cep = cep_service.buscar(cep)
        
        if not info_cep:
            return {"erro": f"CEP {cep} não encontrado"}

        uf = info_cep.get("uf", "SP")
        tipo_tarifa = info_cep.get("tipo_tarifa", "Capital")
        cidade = info_cep.get("cidade", "")
        prazo = info_cep.get("prazo", 5)
        seguro_percentual = info_cep.get("seguro_percentual", 0.0066)
        regiao_interior = info_cep.get("regiao_interior")

        glm = self._obter_glm_dropf(uf, peso) if modalidade == "DROPF" else self._obter_glm(uf, tipo_tarifa, peso)
        lucro = self._obter_lucro(peso)
        
        preco_final = glm + lucro
        seguro = round(valor_nf * seguro_percentual, 2) if valor_nf > 100 else 0.0
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