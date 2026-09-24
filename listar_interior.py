from app.services.cep_service import CEPService

c = CEPService()

print("=== SP - Interior ===")
for r in c.dados:
    if r['uf'] == 'SP' and 'Interior' in r['tipo']:
        print(f"SP | {r['cidade']} | {r['tipo']} | {r['inicio']:08d} a {r['fim']:08d}")

print()
print("=== BA - Interior (primeiras 10) ===")
count = 0
for r in c.dados:
    if r['uf'] == 'BA' and 'Interior' in r['tipo']:
        print(f"BA | {r['cidade']} | {r['tipo']} | {r['inicio']:08d} a {r['fim']:08d}")
        count += 1
        if count >= 10:
            break
