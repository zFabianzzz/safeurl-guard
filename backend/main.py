"""
main.py - SafeURL Guard API con panel de administrador
"""
import logging
import os
from fastapi import FastAPI, Query, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List

from services.analyzer import get_analyzer
from database.db import (
    init_db, guardar_analisis, obtener_historial, obtener_estadisticas,
    limpiar_historial, registrar_dispositivo, obtener_dispositivos,
    agregar_blacklist, eliminar_blacklist, obtener_blacklist, verificar_blacklist,
    verificar_admin, crear_sesion, verificar_sesion, cerrar_sesion,
    actualizar_nombre_dispositivo, marcar_desinstalado, eliminar_dispositivos
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SafeURL Guard API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Modelos ───────────────────────────────────────────────────────────────────

class URLRequest(BaseModel):
    url: str
    device_id: str = "unknown"
    guardar: bool = True


class AdminLogin(BaseModel):
    password: str


class BlacklistRequest(BaseModel):
    device_id: str
    patron: str
    tipo: str = "palabra"


class NombreDispositivoRequest(BaseModel):
    device_id: str
    nombre: str


class PingRequest(BaseModel):
    device_id: str


class EliminarDispositivosRequest(BaseModel):
    device_ids: List[str]


# ── Startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Base de datos inicializada")
    analyzer = get_analyzer()
    if analyzer.model is not None:
        logger.info(f"✅ Modelo listo | Accuracy: {analyzer.metadata.get('accuracy', '?')}")
    else:
        logger.warning("⚠️ Sin modelo — modo heurístico")


# ── Endpoints principales ─────────────────────────────────────────────────────

@app.get("/")
async def home():
    return {"message": "SafeURL Guard API v2.0 funcionando correctamente"}


@app.get("/health")
async def health():
    analyzer = get_analyzer()
    return {
        "status": "ok",
        "modelo": "random_forest" if analyzer.model else "heuristico",
        "modelo_accuracy": analyzer.metadata.get("accuracy", None),
        "version": "2.0.0"
    }


@app.post("/analizar-url")
async def analizar_url(data: URLRequest):
    # Registrar dispositivo
    if data.device_id and data.device_id != "unknown":
        registrar_dispositivo(data.device_id)

    # Verificar blacklist PRIMERO (antes del ML)
    bl = verificar_blacklist(data.url, data.device_id)
    if bl["bloqueado"]:
        result = {
            "url": data.url,
            "dominio": data.url.split("/")[2] if "://" in data.url else data.url,
            "clasificacion": "Bloqueado por admin",
            "riesgo": 100,
            "accion": "Bloqueado",
            "modelo": "blacklist",
            "probabilidades": {},
            "blacklist_patron": bl["patron"],
            "admin_block": True,
        }
        if data.guardar:
            guardar_analisis(result, data.device_id)
        return result

    # Análisis ML normal
    analyzer = get_analyzer()
    result = analyzer.analyze(data.url)

    if data.guardar:
        try:
            guardar_analisis(result, data.device_id)
        except Exception as e:
            logger.error(f"Error guardando: {e}")

    return result


@app.get("/blacklist/{device_id}")
async def get_blacklist_device(device_id: str):
    """La extensión consulta su blacklist al iniciar."""
    return obtener_blacklist(device_id)


# ── Endpoints de dispositivo (públicos, los llama la extensión) ──────────────

@app.post("/dispositivo/nombre")
async def actualizar_nombre(data: NombreDispositivoRequest):
    nombre_limpio = data.nombre.strip()[:50]
    actualizar_nombre_dispositivo(data.device_id, nombre_limpio)
    return {"message": "Nombre actualizado"}


@app.post("/dispositivo/ping")
async def dispositivo_ping(data: PingRequest):
    registrar_dispositivo(data.device_id)
    return {"message": "ok"}


@app.get("/dispositivo/desinstalado", response_class=HTMLResponse)
async def dispositivo_desinstalado(device_id: str = ""):
    if device_id:
        marcar_desinstalado(device_id)
    return """
    <html><body style="font-family:sans-serif;text-align:center;padding:60px;background:#0a0e1a;color:#cdd9e8">
        <h2>👋 Gracias por usar SafeURL Guard</h2>
        <p>Lamentamos verte partir. Si tuviste algún problema, cuéntanos qué mejorar.</p>
    </body></html>
    """


# ── Admin endpoints ───────────────────────────────────────────────────────────

def verificar_token_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autorizado")
    token = authorization.replace("Bearer ", "")
    if not verificar_sesion(token):
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    return token


@app.post("/admin/login")
async def admin_login(data: AdminLogin):
    if not verificar_admin(data.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    token = crear_sesion()
    return {"token": token, "message": "Sesión iniciada correctamente"}


@app.post("/admin/logout")
async def admin_logout(token: str = None, authorization: str = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        t = authorization.replace("Bearer ", "")
        cerrar_sesion(t)
    return {"message": "Sesión cerrada"}


@app.get("/admin/dispositivos")
async def admin_dispositivos(authorization: str = Header(None)):
    verificar_token_admin(authorization)
    return obtener_dispositivos()


@app.post("/admin/dispositivos/eliminar")
async def admin_eliminar_dispositivos(data: EliminarDispositivosRequest, authorization: str = Header(None)):
    verificar_token_admin(authorization)
    if not data.device_ids:
        raise HTTPException(status_code=400, detail="No se especificaron dispositivos")
    eliminar_dispositivos(data.device_ids)
    return {"message": f"{len(data.device_ids)} dispositivo(s) eliminado(s), junto con su historial"}


@app.get("/admin/historial")
async def admin_historial(
    device_id: str = Query(default=None),
    limit: int = Query(default=100),
    authorization: str = Header(None)
):
    verificar_token_admin(authorization)
    return obtener_historial(device_id=device_id, limit=limit)


@app.get("/admin/estadisticas")
async def admin_estadisticas(authorization: str = Header(None)):
    verificar_token_admin(authorization)
    stats = obtener_estadisticas()
    analyzer = get_analyzer()
    stats["modelo_accuracy"] = analyzer.metadata.get("accuracy", None)
    return stats


@app.post("/admin/blacklist")
async def admin_agregar_blacklist(data: BlacklistRequest, authorization: str = Header(None)):
    verificar_token_admin(authorization)
    agregar_blacklist(data.device_id, data.patron, data.tipo)
    return {"message": f"Patrón '{data.patron}' agregado a blacklist de {data.device_id}"}


@app.delete("/admin/blacklist/{blacklist_id}")
async def admin_eliminar_blacklist(blacklist_id: int, authorization: str = Header(None)):
    verificar_token_admin(authorization)
    eliminar_blacklist(blacklist_id)
    return {"message": "Entrada eliminada de la blacklist"}


@app.get("/admin/blacklist")
async def admin_ver_blacklist(
    device_id: str = Query(default=None),
    authorization: str = Header(None)
):
    verificar_token_admin(authorization)
    return obtener_blacklist(device_id)


@app.delete("/admin/historial/{device_id}")
async def admin_limpiar_historial(device_id: str, authorization: str = Header(None)):
    verificar_token_admin(authorization)
    limpiar_historial(device_id=device_id if device_id != "all" else None)
    return {"message": "Historial eliminado"}


# ── Panel admin HTML ──────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    with open(os.path.join(os.path.dirname(__file__), "admin_panel.html"), "r", encoding="utf-8") as f:
        return f.read()