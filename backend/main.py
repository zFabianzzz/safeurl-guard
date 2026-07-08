"""
main.py
API FastAPI para SafeURL Guard - Análisis de URLs con Machine Learning
"""
import logging
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.analyzer import get_analyzer
from database.db import init_db, guardar_analisis, obtener_historial, obtener_estadisticas, limpiar_historial

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SafeURL Guard API",
    description="API de análisis de URLs usando Machine Learning (Random Forest)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class URLRequest(BaseModel):
    url: str
    guardar: bool = True


@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Base de datos inicializada")
    analyzer = get_analyzer()
    if analyzer.model is not None:
        logger.info(f"✅ Modelo listo | Accuracy: {analyzer.metadata.get('accuracy', '?')}")
    else:
        logger.warning("⚠️  Sin modelo entrenado — usando análisis heurístico")


@app.post("/analizar-url")
async def analizar_url(data: URLRequest):
    analyzer = get_analyzer()
    result = analyzer.analyze(data.url)
    if data.guardar:
        try:
            guardar_analisis(result)
        except Exception as e:
            logger.error(f"Error guardando en BD: {e}")
    return result


@app.get("/historial")
async def historial(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    tipo: str = Query(default=None)
):
    return obtener_historial(limit=limit, offset=offset, tipo=tipo)


@app.delete("/historial")
async def limpiar_historial_endpoint():
    limpiar_historial()
    return {"message": "Historial eliminado correctamente"}


@app.get("/estadisticas")
async def estadisticas():
    stats = obtener_estadisticas()
    analyzer = get_analyzer()
    stats["modelo_activo"] = "random_forest" if analyzer.model else "heuristico"
    stats["modelo_accuracy"] = analyzer.metadata.get("accuracy", None)
    return stats


@app.get("/health")
async def health():
    analyzer = get_analyzer()
    return {
        "status": "ok",
        "modelo": "random_forest" if analyzer.model else "heuristico",
        "modelo_accuracy": analyzer.metadata.get("accuracy", None),
        "version": "2.0.0"
    }


@app.get("/")
async def home():
    return {
        "message": "SafeURL Guard API v2.0 funcionando correctamente",
        "endpoints": ["/analizar-url", "/historial", "/estadisticas", "/health"]
    }