from __future__ import annotations

import math

from app.services.cep_service import CEPService
from app.services.frete_calculator import FreteCalculator
from app.services.tarifas_capital_v31 import (
    GLM_CAPITAL_PONTOS,
    LUCRO_FAIXAS,
    PRECO_PROMOCIONAL_CAPITAL,
)
from app.services.tarifas_glm_v31 import PESOS_TABELA, TABELAS_GLM
from tests.referencia_cap_int_v31 import REFERENCIA_CAP_INT


def _primeiro_cep_do_tipo(tipo_alvo: str):
    svc = CEPService()
    for inicio, fim, uf, cidade, tipo, prazo, frap, seguro in svc.dados:
        if tipo == tipo_alvo:
            return f"{inicio:08d}", uf
    raise AssertionError(f"Nenhum CEP para {tipo_alvo}")


def test_cidaten_03309000():
    svc = CEPService()
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


def test_capital1_permanece_suportado_mesmo_sem_cep_atual():
    # A GLM e a CAP x INT possuem Capital 1.
    # A CIDATEN atual não o utiliza, mas o motor mantém suporte.
    for modalidade in ("PACKAGE", ".COM"):
        assert "Capital 1" in TABELAS_GLM[modalidade]
        assert "Capital 1" in REFERENCIA_CAP_INT[modalidade]


def test_cap_x_int_confere_com_glm_liev_em_todas_as_ancoras():
    verificacoes = 0
    for modalidade in ("PACKAGE", ".COM"):
        for tipo, ufs in REFERENCIA_CAP_INT[modalidade].items():
            for uf, referencia in ufs.items():
                tabela = TABELAS_GLM[modalidade][tipo][uf]
                for peso in (1, 5, 10, 20, 30):
                    assert math.isclose(
                        tabela["pesos"][float(peso)],
                        referencia[peso],
                        abs_tol=1e-9,
                    ), (modalidade, tipo, uf, peso)
                    verificacoes += 1

                assert math.isclose(
                    tabela["adicional"],
                    referencia["adicional"],
                    abs_tol=1e-9,
                ), (modalidade, tipo, uf, "adicional")
                verificacoes += 1

    # 2 modalidades x 6 tipos x 27 UFs x 6 pontos.
    assert verificacoes == 1944


def test_glm_completa_tem_pesos_individuais_ate_30():
    assert PESOS_TABELA[:4] == [0.25, 0.5, 0.75, 1.0]
    assert PESOS_TABELA[-1] == 30.0
    assert 23.0 in PESOS_TABELA
    assert 29.0 in PESOS_TABELA


def test_lucro_homologado():
    assert LUCRO_FAIXAS == {
        1: 13.0, 5: 26.0, 10: 44.0, 20: 80.0, 30: 130.0,
        40: 140.0, 50: 150.0, 60: 160.0, 70: 170.0,
        80: 180.0, 90: 190.0, 100: 200.0,
    }


def test_capital_promocional_ate_30():
    calc = FreteCalculator()
    esperados = {
        1: 24.99,
        5: 49.99,
        10: 79.99,
        20: 149.99,
        30: 229.99,
    }
    for peso, esperado in esperados.items():
        dados = calc.calcular("03309-000", peso, "PACKAGE", 100)["dados"]
        assert dados["preco_final"] == esperado
        assert dados["seguro"] == 0.0
        assert dados["_auditoria"]["lucro"] == 0.0
        assert dados["_auditoria"]["regra_calculo"] == "CAPITAL_PROMOCIONAL"


def test_capital_promocional_nao_depende_da_modalidade():
    calc = FreteCalculator()
    pack = calc.calcular("03309-000", 10, "PACKAGE", 100)["dados"]
    com = calc.calcular("03309-000", 10, ".COM", 100)["dados"]
    assert pack["preco_final"] == com["preco_final"] == 79.99


def test_modalidade_altera_glm_quando_regra_e_regional():
    cep, _ = _primeiro_cep_do_tipo("Interior 1")
    calc = FreteCalculator()
    pack = calc.calcular(cep, 10, "PACKAGE", 100)
    com = calc.calcular(cep, 10, ".COM", 100)
    assert pack["success"] and com["success"]
    assert pack["dados"]["_auditoria"]["glm"] != com["dados"]["_auditoria"]["glm"]


def test_peso_23_usa_coluna_23_da_glm_original():
    cep, uf = _primeiro_cep_do_tipo("Interior 2")
    calc = FreteCalculator()
    res = calc.calcular(cep, 23, "PACKAGE", 100)
    assert res["success"], res
    aud = res["dados"]["_auditoria"]
    tabela = TABELAS_GLM["PACKAGE"]["Interior 2"][uf]
    assert aud["peso_tabela_glm"] == 23.0
    assert aud["glm"] == round(tabela["pesos"][23.0], 2)
    assert aud["faixa_lucro"] == 30
    assert aud["lucro"] == 130.0


def test_regional_acima_30_usa_30_mais_kg_adicional():
    cep, uf = _primeiro_cep_do_tipo("Capital 3")
    calc = FreteCalculator()

    for peso in (31, 35, 40, 41, 78, 100):
        res = calc.calcular(cep, peso, "PACKAGE", 100)
        assert res["success"], res
        dados = res["dados"]
        aud = dados["_auditoria"]
        tabela = TABELAS_GLM["PACKAGE"]["Capital 3"][uf]
        adicionais = int(math.ceil(peso - 30))
        glm = round(tabela["pesos"][30.0] + adicionais * tabela["adicional"], 2)

        assert aud["kg_adicionais"] == adicionais
        assert aud["glm"] == glm


def test_capital_acima_30_reproduz_ancoras_cap_x_int():
    calc = FreteCalculator()
    for peso in (40, 50, 60, 70, 80, 90, 100):
        res = calc.calcular("03309-000", peso, "PACKAGE", 100)
        assert res["success"], res
        aud = res["dados"]["_auditoria"]
        assert aud["glm"] == round(GLM_CAPITAL_PONTOS["SP"][peso], 2)


def test_capital_peso_intermediario_e_calculado_como_variavel():
    calc = FreteCalculator()
    dados = calc.calcular("03309-000", 35, "PACKAGE", 100)["dados"]
    aud = dados["_auditoria"]

    incremento = (GLM_CAPITAL_PONTOS["SP"][50] - GLM_CAPITAL_PONTOS["SP"][40]) / 10
    glm30_inferido = GLM_CAPITAL_PONTOS["SP"][40] - 10 * incremento
    esperado = round(glm30_inferido + 5 * incremento, 2)

    assert aud["kg_adicionais"] == 5
    assert aud["glm"] == esperado
    assert aud["faixa_lucro"] == 40
    assert aud["lucro"] == 140.0


def test_nf_controla_ad_valorem_pela_cidaten():
    calc = FreteCalculator()
    sem = calc.calcular("03309-000", 10, "PACKAGE", 100)["dados"]
    com = calc.calcular("03309-000", 10, "PACKAGE", 1000)["dados"]
    assert sem["seguro"] == 0.0
    assert com["seguro"] == 6.60
    assert com["total"] == 86.59


def test_auditoria_interna_informa_fontes_sem_afetar_interface():
    dados = FreteCalculator().calcular("03309-000", 10, "PACKAGE", 100)["dados"]
    aud = dados["_auditoria"]
    assert aud["versao_motor"] == "3.1"
    assert aud["fonte_cep"] == "CIDATEN"
    assert aud["fonte_tarifa"] == "CAP X INT + GLM LIEV"


def test_peso_acima_100_falha():
    res = FreteCalculator().calcular("03309-000", 101, "PACKAGE", 100)
    assert res["success"] is False
