# api/rastreio_simples.py - VERSÃO CORRIGIDA
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Rastreio Jadlog")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/rastreio/{codigo}")
async def buscar_rastreio(codigo: str):
    try:
        logger.info(f"=== BUSCANDO RASTREIO PARA: {codigo} ===")
        
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
        
        response = requests.post(url, data=dados, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return {"success": False, "message": f"Erro: {response.status_code}"}
        
        # ============================================================
        # PARSING COM BEAUTIFULSOUP
        # ============================================================
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrair remessa
        remessa = ""
        remessa_table = soup.find('td', string='Remessa')
        if remessa_table:
            # Procurar o próximo td com o número
            parent = remessa_table.find_parent('tr')
            if parent:
                tds = parent.find_all('td')
                if len(tds) >= 2:
                    remessa = tds[1].get_text(strip=True)
                    logger.info(f"Remessa encontrada: {remessa}")
        
        # ============================================================
        # EXTRAIR EVENTOS
        # ============================================================
        eventos = []
        
        # Método 1: Buscar por small com class txt-data
        for small in soup.find_all('small', class_='txt-data'):
            data_hora = small.get_text(strip=True)
            logger.info(f"Data/hora encontrada: {data_hora}")
            
            # Procurar o texto do evento (pai próximo)
            parent = small.find_parent()
            if parent:
                # Procurar por texto que não seja o small
                for elem in parent.find_all(['p', 'div', 'span']):
                    texto = elem.get_text(strip=True)
                    if texto and texto != data_hora and len(texto) > 5:
                        # Verificar se não é um título
                        if not texto.startswith('Status') and not texto.startswith('Remessa'):
                            # Separar data e hora
                            if ' - ' in data_hora:
                                partes = data_hora.split(' - ')
                                data = partes[0].strip()
                                hora = partes[1].strip() if len(partes) > 1 else ''
                            else:
                                data = data_hora
                                hora = ''
                            
                            eventos.append({
                                "data": data,
                                "hora": hora,
                                "status": texto
                            })
                            logger.info(f"Evento: {data} - {hora} - {texto[:50]}...")
                            break
        
        # Método 2: Se não encontrou, buscar por divs com classe track-status
        if not eventos:
            for div in soup.find_all('div', class_='track-status'):
                texto = div.get_text(strip=True)
                # Procurar data no texto
                data_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*[-–]\s*(\d{2}:\d{2})', texto)
                if data_match:
                    data = data_match.group(1)
                    hora = data_match.group(2)
                    # Remover a data do texto
                    status = texto.replace(data_match.group(0), '').strip()
                    if status and len(status) > 3:
                        eventos.append({
                            "data": data,
                            "hora": hora,
                            "status": status
                        })
                        logger.info(f"Evento (track-status): {data} - {status[:50]}...")
        
        # Método 3: Buscar por padrão no texto (fallback)
        if not eventos:
            logger.info("Tentando extrair por regex no texto...")
            padrao = re.compile(r'(\d{2}/\d{2}/\d{4})\s*[-–]\s*(\d{2}:\d{2})\s*[-–]\s*([^\n]+)')
            matches = padrao.findall(response.text)
            
            for data, hora, status in matches:
                status = status.strip()
                if status and len(status) > 5 and not status.startswith('RASTREAMENTO'):
                    eventos.append({
                        "data": data,
                        "hora": hora,
                        "status": status
                    })
                    logger.info(f"Evento (regex): {data} - {status[:50]}...")
        
        # ============================================================
        # DETERMINAR STATUS
        # ============================================================
        status_atual = "Em trânsito"
        if eventos:
            ultimo = eventos[-1]['status'].lower()
            if 'entregue' in ultimo:
                status_atual = "Entregue"
            elif 'coletado' in ultimo or 'coleta' in ultimo:
                status_atual = "Coletado"
            elif 'saiu para entrega' in ultimo:
                status_atual = "Saiu para entrega"
            elif 'transferência' in ultimo:
                status_atual = "Em transferência"
            
            eventos.reverse()
        
        # ============================================================
        # RESULTADO
        # ============================================================
        if not eventos:
            logger.warning("NENHUM EVENTO ENCONTRADO!")
            return {
                "success": False,
                "message": f"Nenhum evento encontrado para o código {codigo}. Verifique se o código está correto."
            }
        
        logger.info(f"Total de eventos: {len(eventos)}")
        
        return {
            "success": True,
            "codigo": codigo,
            "remessa": remessa,
            "status": status_atual,
            "historico": eventos
        }
        
    except Exception as e:
        logger.error(f"ERRO: {e}")
        return {"success": False, "message": str(e)}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")