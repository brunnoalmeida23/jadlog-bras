# testar_cep.py
import sys
import os

# Adicionar o caminho atual ao sys.path
sys.path.insert(0, os.getcwd())

from app.services.cep_service import CEPService

print("=== TESTANDO CEPSERVICE ===\n")

cep_service = CEPService()

# Testar CEPs
testes = [
    '07071060',    # Guarulhos/SP
    '07803-000',   # Franco da Rocha/SP
    '11700-140',   # Praia Grande/SP
    '20000-000',   # Rio de Janeiro/RJ
    '21000-000',   # Rio de Janeiro/RJ
    '22000-000',   # Rio de Janeiro/RJ
]

for cep in testes:
    resultado = cep_service.buscar(cep)
    if resultado:
        print(f'✅ {cep} -> {resultado["cidade"]}/{resultado["uf"]} - {resultado["tipo_tarifa"]} - {resultado["prazo"]} dias')
    else:
        print(f'❌ {cep} -> NAO ENCONTRADO')