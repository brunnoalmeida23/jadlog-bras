import pandas as pd

df = pd.read_excel("Cidaten_2026.xlsx", sheet_name="Cidaten", header=1)

# Filtra linhas de SP com CEP que começa com 0822
sp = df[df["UF"] == "SP"]
sp_0822 = sp[sp["Cep"].astype(str).str.contains("0822", na=False)]

print(f"Linhas de SP com CEP contendo '0822': {len(sp_0822)}")
print()
for _, row in sp_0822.iterrows():
    print(f"  {row['Cep']:30s} | {row['Localidade']:20s} | {row['Tipo Tarifa']:12s} | {row['% Seguro']}")
