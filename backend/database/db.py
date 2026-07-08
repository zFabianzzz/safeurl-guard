"""
db.py
Base de datos SQLite para guardar historial de análisis.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "safeurl.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea las tablas si no existen."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                dominio TEXT,
                clasificacion TEXT,
                riesgo INTEGER,
                accion TEXT,
                modelo TEXT,
                fecha TEXT DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()


def guardar_analisis(data: dict):
    """Guarda un resultado de análisis en la base de datos."""
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO historial (url, dominio, clasificacion, riesgo, accion, modelo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get("url", ""),
            data.get("dominio", ""),
            data.get("clasificacion", ""),
            data.get("riesgo", 0),
            data.get("accion", ""),
            data.get("modelo", ""),
        ))
        conn.commit()


def obtener_historial(limit: int = 50, offset: int = 0, tipo: str = None):
    """Obtiene el historial de análisis."""
    with get_connection() as conn:
        if tipo and tipo != "Todos":
            rows = conn.execute("""
                SELECT * FROM historial WHERE clasificacion = ?
                ORDER BY fecha DESC LIMIT ? OFFSET ?
            """, (tipo, limit, offset)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM historial ORDER BY fecha DESC LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
        return [dict(r) for r in rows]


def obtener_estadisticas():
    """Obtiene estadísticas de análisis."""
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM historial").fetchone()["c"]
        bloqueadas = conn.execute(
            "SELECT COUNT(*) as c FROM historial WHERE accion='Bloqueado'"
        ).fetchone()["c"]
        por_tipo = conn.execute("""
            SELECT clasificacion, COUNT(*) as total
            FROM historial GROUP BY clasificacion
        """).fetchall()
        return {
            "total": total,
            "bloqueadas": bloqueadas,
            "por_tipo": [dict(r) for r in por_tipo],
        }
def limpiar_historial():
    """Elimina todo el historial de análisis."""
    with get_connection() as conn:
        conn.execute("DELETE FROM historial")
        conn.commit()