import pandas as pd
import json

# Carregar a planilha com o header correto (linha 1)
df = pd.read_excel('resultado interior.xlsx', sheet_name='Mandar Dropoff', header=1)

# Ver as colunas
print("Colunas:", df.columns.tolist())

# Estrutura para armazenar
tabela_dropf = {}

# Colunas de peso (1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100)
# Estão nas colunas 3 a 16
pesos = [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]

for idx, row in df.iterrows():
    uf = row['UF']
    cidade = row['Cidade']
    tipo = row['Interior']
    
    if pd.isna(uf):
        continue
    
    # Extrair valores das colunas de peso
    valores = []
    for peso in pesos:
        # A coluna é identificada pelo nome "Mandar" ou pelo índice
        # Vamos usar os índices das colunas
        val = row.iloc[3 + pesos.index(peso)] if len(row) > 3 + pesos.index(peso) else None
        if pd.notna(val):
            valores.append(float(val))
        else:
            valores.append(None)
    
    # Criar chave
    chave = f"{uf}_{tipo}"
    
    if chave not in tabela_dropf:
        tabela_dropf[chave] = {
            "uf": uf,
            "tipo": tipo,
            "cidade": cidade,
            "pesos": {}
        }
    
    # Adicionar valores
    for i, peso in enumerate(pesos):
        if i < len(valores) and valores[i] is not None:
            tabela_dropf[chave]["pesos"][str(peso)] = valores[i]

# Gerar código Python
print('\n# TABELA DROPF (Mandar Dropoff)')
print('TABELA_DROPF = {')
for chave, dados in tabela_dropf.items():
    print(f'    "{chave}": {{')
    print(f'        "uf": "{dados["uf"]}",')
    print(f'        "tipo": "{dados["tipo"]}",')
    print(f'        "cidade": "{dados["cidade"]}",')
    print(f'        "pesos": {{')
    pesos_str = []
    for peso, valor in dados["pesos"].items():
        pesos_str.append(f'            {peso}: {valor}')
    print(',\n'.join(pesos_str))
    print('        }')
    print('    },')
print('}')