from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routes import (
    api,
    auth,
    consulta,
    home,
    pdf,
    simulador,
)


load_dotenv()


app = FastAPI(
    title="JADLOG BRÁS",
    description="Sistema de Cotação de Frete - Unidade Brás",
    version="1.0.0",
)


session_secret = os.getenv(
    "SESSION_SECRET",
    "jadlog-bras-secret-local-altere-na-vercel",
)


app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="jadlog_session",
    max_age=8 * 60 * 60,
    same_site="lax",
    https_only=os.getenv("VERCEL") == "1",
)


app.include_router(auth.router)
app.include_router(home.router)
app.include_router(simulador.router)
app.include_router(consulta.router)
app.include_router(pdf.router)
app.include_router(api.router)


static_dir = os.path.join(
    os.path.dirname(__file__),
    "static",
)


if os.path.exists(static_dir):
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static",
    )


@app.get("/logo")
async def get_logo():
    logo_path = os.path.join(
        static_dir,
        "logo-jadlog.png",
    )

    if os.path.exists(logo_path):
        return FileResponse(
            logo_path,
            media_type="image/png",
        )

    return {
        "error": "Logo não encontrado",
    }


@app.get("/manifest.json")
async def get_manifest():
    manifest_path = os.path.join(
        static_dir,
        "manifest.json",
    )

    if os.path.exists(manifest_path):
        return FileResponse(
            manifest_path,
            media_type="application/manifest+json",
        )

    return {
        "error": "Manifest não encontrado",
    }


@app.get("/sw.js")
async def get_sw():
    sw_path = os.path.join(
        static_dir,
        "sw.js",
    )

    if os.path.exists(sw_path):
        return FileResponse(
            sw_path,
            media_type="application/javascript",
            headers={
                "Cache-Control": (
                    "no-cache, no-store, must-revalidate"
                ),
            },
        )

    return {
        "error": "Service Worker não encontrado",
    }