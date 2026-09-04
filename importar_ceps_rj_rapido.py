# importar_ceps_rj_rapido.py
import pandas as pd
import re

print("=" * 60)
print("IMPORTADOR DE CEPs DO RJ (VERSÃO RÁPIDA)")
print("=" * 60)

CEPS_RAW = """
# COLE SEUS CEPs AQUI (remova a linha "CEPs do RJ:")
ANGRA DOS REIS: 23954971 a 23954989 - Capital 2
ANGRA DOS REIS: 23954970 a 23954970 - Interior 1
# ... (todos os outros)
"""

def importar_ceps_rapido(ceps_texto):
    try:
        df = pd.read_excel('Cidaten_2026.xlsx', sheet_name='Cidaten', header=1)
        print("📂 Planilha carregada.")
    except:
        df = pd.DataFrame(columns=['UF', 'Localidade', 'Cep', 'Prazo Rodo', 'Tipo Tarifa', 'Frap (Fob)', '% Seguro'])
        print("📄 Nova planilha criada.")

    # Criar um conjunto com os registros existentes para busca rápida
    existentes = set()
    for _, row in df.iterrows():
        existentes.add((row['Localidade'], row['Cep']))

    novas_linhas = []
    linhas = ceps_texto.strip().split('\n')
    total = len(linhas)
    
    print(f"📊 Processando {total} linhas...")

    for i, linha in enumerate(linhas):
        linha = linha.strip()
        if not linha or linha.startswith('#'):
            continue

        match = re.match(r'(.+?):\s*(.+?)\s*a\s*(.+?)\s*-\s*(.+)', linha)
        if not match:
            continue

        cidade = match.group(1).strip().upper()
        cep_ini = match.group(2).strip()
        cep_fim = match.group(3).strip()
        tipo = match.group(4).strip()

        # Determinar prazo
        if "Capital 1" in tipo:
            prazo = 3
        elif "Capital 2" in tipo:
            prazo = 4
        elif "Capital 3" in tipo:
            prazo = 5
        elif "Interior 1" in tipo:
            prazo = 5
        elif "Interior 2" in tipo:
            prazo = 6
        elif "Interior 3" in tipo:
            prazo = 7
        else:
            prazo = 5

        cep_str = cep_ini if cep_ini == cep_fim else f"{cep_ini} a {cep_fim}"

        # Verificar duplicata (busca rápida)
        if (cidade, cep_str) not in existentes:
            novas_linhas.append({
                'UF': 'RJ',
                'Localidade': cidade,
                'Cep': cep_str,
                'Prazo Rodo': prazo,
                'Tipo Tarifa': tipo,
                'Frap (Fob)': 'Nao',
                '% Seguro': 0.0066
            })
            
        # Mostrar progresso a cada 100 linhas
        if (i + 1) % 100 == 0:
            print(f"⏳ Processados {i + 1}/{total} CEPs...")

    if novas_linhas:
        df_novo = pd.DataFrame(novas_linhas)
        df = pd.concat([df, df_novo], ignore_index=True)
        df.to_excel('Cidaten_2026.xlsx', sheet_name='Cidaten', index=False, header=True)
        print(f"\n✅ {len(novas_linhas)} CEPs adicionados!")
        print(f"📊 Total: {len(df)} CEPs")
    else:
        print("\n⚠️ Nenhum CEP novo.")

if __name__ == "__main__":
    print("\n📥 Importando...\n")
    importar_ceps_rapido(CEPS_RAW)
    print("\n✅ Concluído!")
    print("\n🔍 Teste: python testar_cep.py")