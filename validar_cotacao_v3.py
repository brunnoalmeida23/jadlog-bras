# validar_cotacao_v3.py
import argparse
import json
from app.services.frete_calculator import FreteCalculator

parser = argparse.ArgumentParser(description="Validador interno do motor Jadlog Brás V3")
parser.add_argument("cep")
parser.add_argument("peso", type=float)
parser.add_argument("modalidade", choices=["PACKAGE", ".COM", "COM"])
parser.add_argument("valor_nf", type=float)
args = parser.parse_args()

resultado = FreteCalculator().calcular(
    args.cep, args.peso, args.modalidade, args.valor_nf
)
print(json.dumps(resultado, ensure_ascii=False, indent=2))
