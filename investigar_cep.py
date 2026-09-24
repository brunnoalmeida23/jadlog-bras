from app.services.cep_service import CEPService

c = CEPService()

# Simula o buscar para o CEP 08220000
cep_int = 8220000

candidatos = [
    r for r in c.dados
    if r["inicio"] <= cep_int <= r["fim"]
]

candidatos.sort(key=lambda r: r["amplitude"])

print(f"CEP 08220-000 encontrado em {len(candidatos)} linhas:")
for r in candidatos[:10]:
    print(f"  {r['inicio']:08d} a {r['fim']:08d} | {r['cidade']} | {r['tipo']} | amplitude {r['amplitude']}")
