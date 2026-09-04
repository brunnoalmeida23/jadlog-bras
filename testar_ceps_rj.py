# testar_ceps_rj.py
import sys
import os
sys.path.insert(0, os.getcwd())

from app.services.cep_service import CEPService

cep_service = CEPService()

print('=== TESTANDO CEPs DO RJ ===\n')

testes = [
    '23954971',  # Angra dos Reis
    '28970000',  # Araruama
    '27200001',  # Volta Redonda
    '23800001',  # Itaguaí
    '24800001',  # Itaboraí
    '24000001',  # Niterói
    '25845000',  # Areal
    '28300000',  # Itaperuna
    '27500001',  # Resende
    '21000000',  # Rio de Janeiro (referência)
]

for cep in testes:
    resultado = cep_service.buscar(cep)
    if resultado:
        print(f'✅ {cep} -> {resultado["cidade"]}/{resultado["uf"]} - {resultado["tipo_tarifa"]} - {resultado["prazo"]} dias')
    else:
        print(f'❌ {cep} -> NAO ENCONTRADO')