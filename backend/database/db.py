"""
db.py - Base de datos para SafeURL Guard con soporte multi-dispositivo y panel admin.

Funciona en dos modos, sin que haga falta tocar el código ni configurar nada
a mano:

  - Si existe la variable de entorno DATABASE_URL (como en producción, en
    Render, apuntando a Neon) -> usa PostgreSQL.
  - Si NO existe esa variable (por ejemplo, corriendo en la computadora de
    alguien en un laboratorio) -> usa automáticamente un archivo SQLite
    local (safeurl_local.db) que se crea solo, sin instalar nada.
"""
import os
import hashlib
import secrets
from urllib.parse import unquote

DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
else:
    import sqlite3
    SQLITE_PATH = os.path.join(os.path.dirname(__file__), "safeurl_local.db")


def get_connection():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        cur = conn.cursor()

        if USE_POSTGRES:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS historial (
                    id SERIAL PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    dominio TEXT,
                    clasificacion TEXT,
                    riesgo INTEGER,
                    accion TEXT,
                    modelo TEXT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dispositivos (
                    device_id TEXT PRIMARY KEY,
                    nombre TEXT,
                    primera_vez TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultima_vez TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_urls INTEGER DEFAULT 0
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blacklist (
                    id SERIAL PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    patron TEXT NOT NULL,
                    tipo TEXT DEFAULT 'palabra',
                    creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_sessions (
                    token TEXT PRIMARY KEY,
                    creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expira TIMESTAMP
                )
            """)
            # Migración defensiva por si se reutiliza una base con schema viejo
            cur.execute("ALTER TABLE historial ADD COLUMN IF NOT EXISTS device_id TEXT NOT NULL DEFAULT 'unknown'")
            cur.execute("ALTER TABLE dispositivos ADD COLUMN IF NOT EXISTS total_urls INTEGER DEFAULT 0")
            cur.execute("ALTER TABLE dispositivos ADD COLUMN IF NOT EXISTS nombre TEXT")
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS historial (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    dominio TEXT,
                    clasificacion TEXT,
                    riesgo INTEGER,
                    accion TEXT,
                    modelo TEXT,
                    fecha TEXT DEFAULT (datetime('now','localtime'))
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dispositivos (
                    device_id TEXT PRIMARY KEY,
                    nombre TEXT,
                    primera_vez TEXT DEFAULT (datetime('now','localtime')),
                    ultima_vez TEXT DEFAULT (datetime('now','localtime')),
                    total_urls INTEGER DEFAULT 0
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blacklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    patron TEXT NOT NULL,
                    tipo TEXT DEFAULT 'palabra',
                    creado TEXT DEFAULT (datetime('now','localtime'))
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_sessions (
                    token TEXT PRIMARY KEY,
                    creado TEXT DEFAULT (datetime('now','localtime')),
                    expira TEXT
                )
            """)
            _migrar_columnas_sqlite(cur)

        conn.commit()
    finally:
        conn.close()

    _crear_admin_por_defecto()


def _migrar_columnas_sqlite(cur):
    """SQLite no soporta 'ADD COLUMN IF NOT EXISTS', así que revisamos a mano."""
    columnas_historial = [row[1] for row in cur.execute("PRAGMA table_info(historial)").fetchall()]
    if "device_id" not in columnas_historial:
        cur.execute("ALTER TABLE historial ADD COLUMN device_id TEXT NOT NULL DEFAULT 'unknown'")

    columnas_dispositivos = [row[1] for row in cur.execute("PRAGMA table_info(dispositivos)").fetchall()]
    if "total_urls" not in columnas_dispositivos:
        cur.execute("ALTER TABLE dispositivos ADD COLUMN total_urls INTEGER DEFAULT 0")
    if "nombre" not in columnas_dispositivos:
        cur.execute("ALTER TABLE dispositivos ADD COLUMN nombre TEXT")


def _crear_admin_por_defecto():
    """Crea la contraseña de admin si no existe en el archivo .env o variable de entorno."""
    pass


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verificar_admin(password: str) -> bool:
    admin_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")
    if not admin_hash:
        default_hash = hash_password("SafeURL@Admin2024!")
        return hash_password(password) == default_hash
    return hash_password(password) == admin_hash


def crear_sesion() -> str:
    token = secrets.token_urlsafe(32)
    conn = get_connection()
    try:
        cur = conn.cursor()
        if USE_POSTGRES:
            cur.execute("""
                INSERT INTO admin_sessions (token, expira)
                VALUES (%s, CURRENT_TIMESTAMP + INTERVAL '8 hours')
            """, (token,))
        else:
            cur.execute("""
                INSERT INTO admin_sessions (token, expira)
                VALUES (?, datetime('now','localtime','+8 hours'))
            """, (token,))
        conn.commit()
    finally:
        conn.close()
    return token


def verificar_sesion(token: str) -> bool:
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cur.execute(f"""
            SELECT token FROM admin_sessions
            WHERE token = {ph} AND expira > CURRENT_TIMESTAMP
        """, (token,)) if USE_POSTGRES else cur.execute(f"""
            SELECT token FROM admin_sessions
            WHERE token = {ph} AND expira > datetime('now','localtime')
        """, (token,))
        row = cur.fetchone()
        return row is not None
    finally:
        conn.close()


def cerrar_sesion(token: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cur.execute(f"DELETE FROM admin_sessions WHERE token = {ph}", (token,))
        conn.commit()
    finally:
        conn.close()


# ── Dispositivos ──────────────────────────────────────────────────────────────

def registrar_dispositivo(device_id: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cur.execute(f"SELECT device_id FROM dispositivos WHERE device_id = {ph}", (device_id,))
        existing = cur.fetchone()
        if existing:
            if USE_POSTGRES:
                cur.execute(f"UPDATE dispositivos SET ultima_vez = CURRENT_TIMESTAMP WHERE device_id = {ph}", (device_id,))
            else:
                cur.execute(f"UPDATE dispositivos SET ultima_vez = datetime('now','localtime') WHERE device_id = {ph}", (device_id,))
        else:
            cur.execute(f"INSERT INTO dispositivos (device_id) VALUES ({ph})", (device_id,))
        conn.commit()
    finally:
        conn.close()


def obtener_dispositivos():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                d.device_id AS device_id,
                d.nombre AS nombre,
                d.primera_vez AS primera_vez,
                d.ultima_vez AS ultima_vez,
                COUNT(h.id) AS total_urls
            FROM dispositivos d
            LEFT JOIN historial h ON d.device_id = h.device_id
            GROUP BY d.device_id, d.nombre, d.primera_vez, d.ultima_vez
            ORDER BY d.ultima_vez DESC
        """)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── Historial ─────────────────────────────────────────────────────────────────

def guardar_analisis(data: dict, device_id: str = "unknown"):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cur.execute(f"""
            INSERT INTO historial (device_id, url, dominio, clasificacion, riesgo, accion, modelo)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        """, (
            device_id,
            data.get("url", ""),
            data.get("dominio", ""),
            data.get("clasificacion", ""),
            data.get("riesgo", 0),
            data.get("accion", ""),
            data.get("modelo", ""),
        ))
        if USE_POSTGRES:
            cur.execute(f"""
                UPDATE dispositivos SET ultima_vez = CURRENT_TIMESTAMP, total_urls = total_urls + 1
                WHERE device_id = {ph}
            """, (device_id,))
        else:
            cur.execute(f"""
                UPDATE dispositivos SET ultima_vez = datetime('now','localtime'), total_urls = total_urls + 1
                WHERE device_id = {ph}
            """, (device_id,))
        conn.commit()
    finally:
        conn.close()


def obtener_historial(device_id: str = None, limit: int = 100):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        if device_id:
            cur.execute(f"""
                SELECT * FROM historial WHERE device_id = {ph}
                ORDER BY fecha DESC LIMIT {ph}
            """, (device_id, limit))
        else:
            cur.execute(f"SELECT * FROM historial ORDER BY fecha DESC LIMIT {ph}", (limit,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def obtener_estadisticas():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM historial")
        total = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) as c FROM historial WHERE accion='Bloqueado'")
        bloqueadas = cur.fetchone()["c"]

        cur.execute("SELECT COUNT(*) as c FROM dispositivos")
        dispositivos = cur.fetchone()["c"]

        cur.execute("SELECT clasificacion, COUNT(*) as total FROM historial GROUP BY clasificacion")
        por_tipo = cur.fetchall()

        return {
            "total": total,
            "bloqueadas": bloqueadas,
            "dispositivos": dispositivos,
            "por_tipo": [dict(r) for r in por_tipo],
        }
    finally:
        conn.close()


def limpiar_historial(device_id: str = None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        if device_id:
            cur.execute(f"DELETE FROM historial WHERE device_id = {ph}", (device_id,))
        else:
            cur.execute("DELETE FROM historial")
        conn.commit()
    finally:
        conn.close()


# ── Blacklist ─────────────────────────────────────────────────────────────────

def agregar_blacklist(device_id: str, patron: str, tipo: str = "palabra"):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cur.execute(f"INSERT INTO blacklist (device_id, patron, tipo) VALUES ({ph}, {ph}, {ph})",
                    (device_id, patron.lower().strip(), tipo))
        conn.commit()
    finally:
        conn.close()


def eliminar_blacklist(blacklist_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cur.execute(f"DELETE FROM blacklist WHERE id = {ph}", (blacklist_id,))
        conn.commit()
    finally:
        conn.close()


def obtener_blacklist(device_id: str = None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        if device_id:
            cur.execute(f"""
                SELECT * FROM blacklist
                WHERE device_id = {ph} OR device_id = '*'
                ORDER BY creado DESC
            """, (device_id,))
        else:
            cur.execute("SELECT * FROM blacklist ORDER BY creado DESC")
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def verificar_blacklist(url: str, device_id: str) -> dict:
    """Verifica si una URL está en la blacklist del dispositivo o global.

    Decodifica la URL antes de comparar, para que funcione también con
    palabras que tienen tildes, ñ u otros caracteres especiales (las URLs
    llegan "codificadas", por ejemplo "Patrón" llega como "Patr%C3%B3n").
    """
    url_decodificada = unquote(url)
    url_lower = url_decodificada.lower()
    blacklist = obtener_blacklist(device_id)
    for item in blacklist:
        if item["patron"] in url_lower:
            return {"bloqueado": True, "patron": item["patron"], "id": item["id"]}
    return {"bloqueado": False}