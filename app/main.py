# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.routes import home, simulador, consulta, api, rastreio
from app.routes.auth import router as auth_router

app = FastAPI(
    title="JADLOG BRÁS",
    description="Sistema de Cotação de Frete - Unidade Brás",
    version="1.0.0"
)

# Rotas
app.include_router(home.router)
app.include_router(simulador.router)
app.include_router(consulta.router)
app.include_router(api.router)
app.include_router(rastreio.router)
app.include_router(auth_router)

# Servir arquivos estáticos
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/logo")
async def get_logo():
    logo_path = os.path.join(static_dir, "logo.png")
    if os.path.exists(logo_path):
        return FileResponse(logo_path)
    return {"error": "Logo não encontrado"}


@app.get("/manifest.json")
async def get_manifest():
    manifest_path = os.path.join(static_dir, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path)
    return {"error": "Manifest não encontrado"}


@app.get("/sw.js")
async def get_sw():
    sw_path = os.path.join(static_dir, "sw.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path)
    return {"error": "Service Worker não encontrado"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)