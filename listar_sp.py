import pandas as pd

df = pd.read_excel("Cidaten_2026.xlsx", sheet_name="Cidaten", header=1)

sp = df[df["UF"] == "SP"]

# Extrai o CEP inicial de cada linha
def extrair_inicio(cep_str):
    import re
    nums = re.findall(r"\d+", str(cep_str))
    return int(nums[0]) if nums else 0

sp = sp.copy()
sp["inicio"] = sp["Cep"].apply(extrair_inicio)
sp = sp.sort_values("inicio")

print(f"Total de linhas de SP: {len(sp)}")
print()
print("=== Linhas de SP (todas) ===")
for _, row in sp.iterrows():
    print(f"  {row['Cep']:30s} | {row['Localidade']:25s} | {row['Tipo Tarifa']:12s}")
