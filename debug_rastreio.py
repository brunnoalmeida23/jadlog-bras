# debug_rastreio.py
import requests
import re

codigo = "18137200312411"

print(f"=== BUSCANDO RASTREIO PARA CÓDIGO: {codigo} ===")

url = "https://www.jadlog.com.br/jadlog/rastreio"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://www.jadlog.com.br',
    'Referer': 'https://www.jadlog.com.br/jadlog/captcha',
}

dados = {'cte': codigo}

print("Enviando requisição...")
response = requests.post(url, data=dados, headers=headers, timeout=30)

print(f"Status: {response.status_code}")
print(f"Tamanho do HTML: {len(response.text)} caracteres")

# Salvar o HTML
with open('debug_jadlog.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("HTML salvo em debug_jadlog.html")

# Procurar por padrões
print("\n=== PROcurando POR PADRÕES ===")

# Procurar por Remessa
remessa_match = re.search(r'Remessa\s*[\n\r]*\s*(\d+)', response.text)
if remessa_match:
    print(f"✅ Remessa encontrada: {remessa_match.group(1)}")
else:
    print("❌ Remessa NÃO encontrada")

# Procurar por datas
datas = re.findall(r'\d{2}/\d{2}/\d{4}', response.text)
print(f"Datas encontradas: {len(datas)}")
if datas:
    print(f"Primeiras datas: {datas[:5]}")

# Procurar por eventos
padrao = re.compile(r'(\d{2}/\d{2}/\d{4})\s*[-–]\s*(\d{2}:\d{2})\s*[-–]\s*([^\n]+)')
matches = padrao.findall(response.text)
print(f"Matches de evento: {len(matches)}")

for data, hora, status in matches[:5]:  # Mostrar os 5 primeiros
    print(f"  - {data} - {hora} - {status[:50]}...")

# Mostrar trecho do HTML que contém "Remessa" ou datas
print("\n=== TRECHOS DO HTML ===")

# Encontrar onde está "Remessa"
if "Remessa" in response.text:
    pos = response.text.find("Remessa")
    print(f"Trecho com 'Remessa':")
    print(response.text[max(0, pos-50):pos+200])

# Encontrar primeiro bloco com data
if datas:
    pos = response.text.find(datas[0])
    print(f"\nTrecho com primeira data ({datas[0]}):")
    print(response.text[max(0, pos-50):pos+200])

print("\n=== FIM ===")