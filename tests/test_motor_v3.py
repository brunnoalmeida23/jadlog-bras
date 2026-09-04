from __future__ import annotations

import math

from app.services.cep_service import CEPService
from app.services.frete_calculator import FreteCalculator
from app.services.tarifas_capital_v3 import (
    GLM_CAPITAL_PONTOS,
    LUCRO_FAIXAS,
    PRECO_PROMOCIONAL_CAPITAL,
)
from app.services.tarifas_glm_v3 import PESOS_TABELA, TABELAS_GLM


def _primeiro_cep_do_tipo(tipo_alvo: str):
    svc = CEPService()
    for inicio, fim, uf, cidade, tipo, prazo, frap, seguro in svc.dados:
        if tipo == tipo_alvo:
            return f"{inicio:08d}", uf
    raise AssertionError(f"Nenhum CEP para {tipo_alvo}")


def test_cidaten_03309000_e_estrutura():
    svc = CEPService()
    assert len(svc.dados) == 14158
    info = svc.buscar("03309-000")
    assert info
    assert info["uf"] == "SP"
    assert info["cidade"] == "SAO PAULO"
    assert info["tipo_tarifa"] == "Capital"
    assert info["prazo"] == 4
    assert math.isclose(info["seguro_percentual"], 0.0066, abs_tol=1e-12)


def test_tipos_cidaten_sao_suportados():
    svc = CEPService()
    tipos = {r[4] for r in svc.dados}
    assert tipos == {
        "Capital", "Capital 2", "Capital 3",
        "Interior 1", "Interior 2", "Interior 3",
    }
    suportados = set(FreteCalculator.TIPOS_GLM) | {"Capital"}
    assert tipos <= suportados


def test_glm_completa_tem_todas_modalidades_e_pesos():
    assert set(TABELAS_GLM) == {"PACKAGE", ".COM"}
    assert PESOS_TABELA[:4] == [0.25, 0.5, 0.75, 1.0]
    assert PESOS_TABELA[-1] == 30.0
    for modalidade in ("PACKAGE", ".COM"):
        for tipo in ("Capital 1", "Capital 2", "Capital 3", "Interior 1", "Interior 2", "Interior 3"):
            assert tipo in TABELAS_GLM[modalidade]


def test_valores_fonte_sp_capital3():
    # Pontos lidos da GLM original; protege contra transcrição errada.
    pack = TABELAS_GLM["PACKAGE"]["Capital 3"]["SP"]
    com = TABELAS_GLM[".COM"]["Capital 3"]["SP"]
    assert math.isclose(pack["pesos"][30.0], 37.2328, abs_tol=1e-9)
    assert math.isclose(pack["adicional"], 1.0044, abs_tol=1e-9)
    assert math.isclose(com["pesos"][30.0], 68.4664, abs_tol=1e-9)
    assert math.isclose(com["adicional"], 6.6636, abs_tol=1e-9)


def test_lucro_homologado():
    assert LUCRO_FAIXAS == {
        1: 13.0, 5: 26.0, 10: 44.0, 20: 80.0, 30: 130.0,
        40: 140.0, 50: 150.0, 60: 160.0, 70: 170.0,
        80: 180.0, 90: 190.0, 100: 200.0,
    }


def test_capital_promocional_10kg():
    dados = FreteCalculator().calcular("03309-000", 10, "PACKAGE", 100)["dados"]
    assert dados["preco_final"] == 79.99
    assert dados["total"] == 79.99
    assert dados["_auditoria"]["lucro"] == 0.0
    assert dados["_auditoria"]["regra_calculo"] == "CAPITAL_PROMOCIONAL"


def test_modalidade_altera_glm_regional():
    cep, _ = _primeiro_cep_do_tipo("Interior 1")
    calc = FreteCalculator()
    pack = calc.calcular(cep, 10, "PACKAGE", 100)
    com = calc.calcular(cep, 10, ".COM", 100)
    assert pack["success"] and com["success"]
    assert pack["dados"]["_auditoria"]["modalidade_aplicada"] == "PACKAGE"
    assert com["dados"]["_auditoria"]["modalidade_aplicada"] == ".COM"
    # As duas fontes são tabelas independentes.
    assert pack["dados"]["_auditoria"]["glm"] != com["dados"]["_auditoria"]["glm"]


def test_peso_regional_variavel_acima_30():
    cep, uf = _primeiro_cep_do_tipo("Capital 3")
    calc = FreteCalculator()
    resultado = calc.calcular(cep, 35, "PACKAGE", 100)
    assert resultado["success"], resultado
    dados = resultado["dados"]
    aud = dados["_auditoria"]
    tabela = TABELAS_GLM["PACKAGE"]["Capital 3"][uf]

    esperado_glm = round(tabela["pesos"][30.0] + 5 * tabela["adicional"], 2)
    assert aud["kg_adicionais"] == 5
    assert aud["glm"] == esperado_glm
    assert aud["faixa_lucro"] == 40
    assert aud["lucro"] == 140.0
    assert dados["preco_final"] == round(esperado_glm + 140.0, 2)


def test_pesos_31_35_40_41_78_100_nao_sao_casos_fixos():
    cep, uf = _primeiro_cep_do_tipo("Interior 2")
    calc = FreteCalculator()
    tabela = TABELAS_GLM[".COM"]["Interior 2"][uf]

    for peso in (31, 35, 40, 41, 78, 100):
        res = calc.calcular(cep, peso, ".COM", 100)
        assert res["success"], res
        aud = res["dados"]["_auditoria"]
        adicionais = int(math.ceil(peso - 30))
        esperado = round(tabela["pesos"][30.0] + adicionais * tabela["adicional"], 2)
        assert aud["kg_adicionais"] == adicionais
        assert aud["glm"] == esperado


def test_nf_controla_ad_valorem():
    calc = FreteCalculator()
    sem = calc.calcular("03309-000", 10, "PACKAGE", 100)["dados"]
    com = calc.calcular("03309-000", 10, "PACKAGE", 1000)["dados"]
    assert sem["seguro"] == 0.0
    assert com["seguro"] == 6.60
    assert com["total"] == 86.59


def test_capital_acima_30_reproduz_pontos_da_planilha():
    calc = FreteCalculator()
    # 03309-000 => SP / Capital
    for peso in (40, 50, 60, 70, 80, 90, 100):
        dados = calc.calcular("03309-000", peso, "PACKAGE", 100)["dados"]
        assert dados["_auditoria"]["glm"] == round(GLM_CAPITAL_PONTOS["SP"][peso], 2)


def test_capital_35_e_variavel():
    calc = FreteCalculator()
    dados = calc.calcular("03309-000", 35, "PACKAGE", 100)["dados"]
    aud = dados["_auditoria"]

    adicional = (GLM_CAPITAL_PONTOS["SP"][50] - GLM_CAPITAL_PONTOS["SP"][40]) / 10
    glm30 = GLM_CAPITAL_PONTOS["SP"][40] - 10 * adicional
    esperado = round(glm30 + 5 * adicional, 2)

    assert aud["kg_adicionais"] == 5
    assert aud["glm"] == esperado
    assert aud["lucro"] == 140.0


def test_peso_acima_100_falha_em_vez_de_inventar_regra():
    res = FreteCalculator().calcular("03309-000", 101, "PACKAGE", 100)
    assert res["success"] is False
