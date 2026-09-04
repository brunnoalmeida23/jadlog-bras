# extrair_tabela_frete.py
import pandas as pd
import json

# Carregar a planilha
df = pd.read_excel("APP FEITO MANUALMENTE.xlsx", sheet_name="GLM pack", header=4)

# Limpar dados
df = df.dropna(how='all')
df = df.reset_index(drop=True)

# Estrutura para armazenar os dados
tabela_frete = {}

# Mapeamento de colunas para pesos
pesos = [0.25, 0.5, 0.75, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

# Colunas de peso começam na coluna D (índice 3)
colunas_peso = df.columns[3:36]  # D até AK

for idx, row in df.iterrows():
    uf = row['UF']
    tipo_tarifa = row['Tipo de Tarifa']
    regiao = row['Região']
    
    # Pular linhas com UF vazio
    if pd.isna(uf):
        continue
    
    # Extrair valores de peso
    valores = []
    for col in colunas_peso:
        val = row[col]
        if pd.notna(val):
            valores.append(float(val))
        else:
            valores.append(None)
    
    # Extrair Kg Adicional (última coluna)
    kg_adicional = row.iloc[-1] if pd.notna(row.iloc[-1]) else 0
    
    # Criar chave para o dicionário
    chave = f"{uf}_{tipo_tarifa}"
    
    if chave not in tabela_frete:
        tabela_frete[chave] = {
            "uf": uf,
            "tipo": tipo_tarifa,
            "regiao": regiao,
            "pesos": {}
        }
    
    # Adicionar valores
    for i, peso in enumerate(pesos):
        if i < len(valores) and valores[i] is not None:
            tabela_frete[chave]["pesos"][str(peso)] = valores[i]
    
    tabela_frete[chave]["kg_adicional"] = kg_adicional

# Gerar código Python
print("=" * 80)
print("TABELA DE FRETE ATUALIZADA")
print("=" * 80)
print()

print("# app/services/tabela_frete.py")
print("# Tabela extraída de APP FEITO MANUALMENTE.xlsx")
print("# Modalidade: .PACKAGE")
print("# Origem: SP")
print("# Vigência: 16/03/2024")
print()

print("TABELA_FRETE = {")

for chave, dados in tabela_frete.items():
    print(f'    "{chave}": {{')
    print(f'        "uf": "{dados["uf"]}",')
    print(f'        "tipo": "{dados["tipo"]}",')
    print(f'        "regiao": "{dados["regiao"]}",')
    print(f'        "kg_adicional": {dados["kg_adicional"]},')
    print(f'        "pesos": {{')
    
    pesos_str = []
    for peso, valor in dados["pesos"].items():
        pesos_str.append(f'            {peso}: {valor}')
    
    print(",\n".join(pesos_str))
    print("        }")
    print("    },")

print("}")