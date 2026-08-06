# api_rastreio_jadlog.py
import pytesseract
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
import base64
import re
import time
import logging
from typing import List, Optional
from pydantic import BaseModel

# CONFIGURAÇÃO DO TESSERACT
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Rastreio Jadlog", version="1.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EventoRastreio(BaseModel):
    data: str
    hora: str
    status: str

class RastreioResponse(BaseModel):
    success: bool
    codigo: str
    remessa: Optional[str] = None
    status: str
    historico: List[EventoRastreio]

class JadlogRastreio:
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def setup_driver(self):
        """Configura o driver do Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executar em segundo plano
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        logger.info("Driver configurado com sucesso")
    
    def resolver_captcha(self):
        """Resolve o CAPTCHA usando Tesseract OCR"""
        try:
            # Esperar a imagem do captcha carregar
            captcha_img = self.wait.until(
                EC.presence_of_element_located((By.ID, "imgCaptcha"))
            )
            
            # Pegar a URL da imagem
            img_src = captcha_img.get_attribute("src")
            
            if not img_src:
                raise Exception("URL da imagem não encontrada")
            
            # Baixar a imagem
            import requests
            response = requests.get(img_src)
            image = Image.open(io.BytesIO(response.content))
            
            # Pré-processamento
            image = image.convert('L')  # Escala de cinza
            threshold = 150
            image = image.point(lambda x: 0 if x < threshold else 255, '1')
            
            # Reconhecer texto
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            captcha_text = pytesseract.image_to_string(image, config=custom_config)
            captcha_text = re.sub(r'[^A-Z0-9]', '', captcha_text).strip()
            
            logger.info(f"CAPTCHA reconhecido: {captcha_text}")
            return captcha_text
            
        except Exception as e:
            logger.error(f"Erro ao resolver CAPTCHA: {e}")
            return None
    
    def buscar_rastreio(self, codigo: str):
        """Busca o rastreio no site da Jadlog"""
        try:
            # Acessar página de rastreio
            self.driver.get("https://www.jadlog.com.br/jadlog/captcha")
            logger.info("Página de rastreio acessada")
            
            # Tentar resolver o CAPTCHA
            for tentativa in range(3):
                logger.info(f"Tentativa {tentativa + 1} de 3")
                
                captcha_text = self.resolver_captcha()
                if not captcha_text:
                    self.driver.refresh()
                    time.sleep(2)
                    continue
                
                # Preencher formulário
                codigo_input = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "cte"))
                )
                codigo_input.clear()
                codigo_input.send_keys(codigo)
                
                captcha_input = self.driver.find_element(By.NAME, "txtCodigo")
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                
                # Clicar em procurar
                botao = self.driver.find_element(By.NAME, "btnProcurar")
                botao.click()
                
                time.sleep(3)
                
                # Verificar se deu erro
                if "O código digitado é inválido" in self.driver.page_source:
                    logger.warning("CAPTCHA inválido, tentando novamente...")
                    self.driver.refresh()
                    time.sleep(2)
                    continue
                
                # Sucesso! Extrair dados
                return self._extrair_dados(codigo)
            
            raise Exception("Não foi possível resolver o CAPTCHA")
            
        except Exception as e:
            logger.error(f"Erro no rastreio: {e}")
            raise
    
    def _extrair_dados(self, codigo: str):
        """Extrai os dados da página de resultado"""
        page_source = self.driver.page_source
        
        # Extrair remessa
        remessa = ""
        remessa_match = re.search(r'Remessa\s*[\n\r]*\s*(\d+)', page_source)
        if remessa_match:
            remessa = remessa_match.group(1)
        
        # Extrair eventos
        eventos = []
        padrao = re.compile(r'(\d{2}/\d{2}/\d{4})\s*[-–]\s*(\d{2}:\d{2})\s*[-–]\s*([^\n]+)')
        matches = padrao.findall(page_source)
        
        for data, hora, status in matches:
            status = status.strip()
            if status and not status.startswith('RASTREAMENTO') and not status.startswith('Resultados'):
                eventos.append({
                    "data": data,
                    "hora": hora,
                    "status": status
                })
        
        # Status final
        status_atual = "Em trânsito"
        if eventos:
            ultimo = eventos[-1]['status'].lower()
            if 'entregue' in ultimo:
                status_atual = "Entregue"
            elif 'coletado' in ultimo or 'coleta' in ultimo:
                status_atual = "Coletado"
            elif 'caminho' in ultimo or 'saiu para entrega' in ultimo:
                status_atual = "Saiu para entrega"
        
        eventos.reverse()  # Do mais antigo para o mais novo
        
        return {
            "success": True,
            "codigo": codigo,
            "remessa": remessa,
            "status": status_atual,
            "historico": eventos
        }
    
    def close(self):
        if self.driver:
            self.driver.quit()

# Instância global
rastreador = None

@app.on_event("startup")
async def startup_event():
    global rastreador
    try:
        rastreador = JadlogRastreio()
        rastreador.setup_driver()
        logger.info("API Rastreio Jadlog iniciada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao iniciar: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global rastreador
    if rastreador:
        rastreador.close()
        logger.info("API Rastreio Jadlog finalizada")

@app.get("/rastreio/{codigo}")
async def buscar_rastreio(codigo: str):
    """Busca o rastreio de uma encomenda"""
    try:
        global rastreador
        resultado = rastreador.buscar_rastreio(codigo)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)