import json
import sys

from app.services.frete_calculator import FreteCalculator


def main():
    if len(sys.argv) != 5:
        print("Uso: python validar_cotacao_v31.py CEP PESO MODALIDADE VALOR_NF")
        print('Exemplo: python validar_cotacao_v31.py 03309000 35 PACKAGE 100')
        raise SystemExit(2)

    cep = sys.argv[1]
    peso = float(sys.argv[2].replace(",", "."))
    modalidade = sys.argv[3]
    valor_nf = float(sys.argv[4].replace(",", "."))

    resultado = FreteCalculator().calcular(
        cep=cep,
        peso=peso,
        modalidade=modalidade,
        valor_nf=valor_nf,
    )

    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
