import pandas as pd
df = pd.read_excel('Cidaten_2026.xlsx', sheet_name='Cidaten', header=1)
rj = df[df['UF'] == 'RJ']
print('CEPs do RJ:')
for idx, row in rj.iterrows():
    print(f"{row['Localidade']}: {row['Cep']} - {row['Tipo Tarifa']}")