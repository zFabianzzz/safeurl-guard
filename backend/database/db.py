"""
db.py - Base de datos PostgreSQL (Neon) para SafeURL Guard con soporte
multi-dispositivo y panel admin.

Migrado desde SQLite. Mantiene exactamente las mismas funciones que
usaba main.py, para que no haya que tocar el resto del backend.
"""
import os
import hashlib
import secrets

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "Falta la variable de entorno DATABASE_URL. "
            "Configúrala en Render → Environment con el connection string de Neon."
        )
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Historial por dispositivo
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
            # Dispositivos registrados
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dispositivos (
                    device_id TEXT PRIMARY KEY,
                    nombre TEXT,
                    primera_vez TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultima_vez TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_urls INTEGER DEFAULT 0
                )
            """)
            # Blacklist por dispositivo (o global con device_id='*')
            cur.execute("""
                CREATE TABLE IF NOT EXISTS blacklist (
                    id SERIAL PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    patron TEXT NOT NULL,
                    tipo TEXT DEFAULT 'palabra',
                    creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Admin tokens de sesión
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_sessions (
                    token TEXT PRIMARY KEY,
                    creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expira TIMESTAMP
                )
            """)

            # Migración defensiva: agrega columnas si faltaran (por si en el
            # futuro se reutiliza esta base con un schema mas viejo)
            cur.execute("ALTER TABLE historial ADD COLUMN IF NOT EXISTS device_id TEXT NOT NULL DEFAULT 'unknown'")
            cur.execute("ALTER TABLE dispositivos ADD COLUMN IF NOT EXISTS total_urls INTEGER DEFAULT 0")
            cur.execute("ALTER TABLE dispositivos ADD COLUMN IF NOT EXISTS nombre TEXT")

        conn.commit()
    _crear_admin_por_defecto()


def _crear_admin_por_defecto():
    """Crea la contraseña de admin si no existe en el archivo .env o variable de entorno."""
    pass


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verificar_admin(password: str) -> bool:
    admin_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")
    if not admin_hash:
        # Si no hay variable de entorno, usar contraseña por defecto hasheada
        default_hash = hash_password("SafeURL@Admin2024!")
        return hash_password(password) == default_hash
    return hash_password(password) == admin_hash


def crear_sesion() -> str:
    token = secrets.token_urlsafe(32)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO admin_sessions (token, expira)
                VALUES (%s, CURRENT_TIMESTAMP + INTERVAL '8 hours')
            """, (token,))
        conn.commit()
    return token


def verificar_sesion(token: str) -> bool:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT token FROM admin_sessions
                WHERE token = %s AND expira > CURRENT_TIMESTAMP
            """, (token,))
            row = cur.fetchone()
            return row is not None


def cerrar_sesion(token: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM admin_sessions WHERE token = %s", (token,))
        conn.commit()


# ── Dispositivos ──────────────────────────────────────────────────────────────

def registrar_dispositivo(device_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT device_id FROM dispositivos WHERE device_id = %s", (device_id,))
            existing = cur.fetchone()
            if existing:
                cur.execute("""
                    UPDATE dispositivos SET ultima_vez = CURRENT_TIMESTAMP
                    WHERE device_id = %s
                """, (device_id,))
            else:
                cur.execute(
                    "INSERT INTO dispositivos (device_id) VALUES (%s)", (device_id,)
                )
        conn.commit()


def obtener_dispositivos():
    with get_connection() as conn:
        with conn.cursor() as cur:
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


# ── Historial ─────────────────────────────────────────────────────────────────

def guardar_analisis(data: dict, device_id: str = "unknown"):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO historial (device_id, url, dominio, clasificacion, riesgo, accion, modelo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                device_id,
                data.get("url", ""),
                data.get("dominio", ""),
                data.get("clasificacion", ""),
                data.get("riesgo", 0),
                data.get("accion", ""),
                data.get("modelo", ""),
            ))
            cur.execute("""
                UPDATE dispositivos SET ultima_vez = CURRENT_TIMESTAMP,
                total_urls = total_urls + 1
                WHERE device_id = %s
            """, (device_id,))
        conn.commit()


def obtener_historial(device_id: str = None, limit: int = 100):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if device_id:
                cur.execute("""
                    SELECT * FROM historial WHERE device_id = %s
                    ORDER BY fecha DESC LIMIT %s
                """, (device_id, limit))
            else:
                cur.execute("""
                    SELECT * FROM historial ORDER BY fecha DESC LIMIT %s
                """, (limit,))
            rows = cur.fetchall()
            return [dict(r) for r in rows]


def obtener_estadisticas():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as c FROM historial")
            total = cur.fetchone()["c"]

            cur.execute("SELECT COUNT(*) as c FROM historial WHERE accion='Bloqueado'")
            bloqueadas = cur.fetchone()["c"]

            cur.execute("SELECT COUNT(*) as c FROM dispositivos")
            dispositivos = cur.fetchone()["c"]

            cur.execute("""
                SELECT clasificacion, COUNT(*) as total
                FROM historial GROUP BY clasificacion
            """)
            por_tipo = cur.fetchall()

            return {
                "total": total,
                "bloqueadas": bloqueadas,
                "dispositivos": dispositivos,
                "por_tipo": [dict(r) for r in por_tipo],
            }


def limpiar_historial(device_id: str = None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if device_id:
                cur.execute("DELETE FROM historial WHERE device_id = %s", (device_id,))
            else:
                cur.execute("DELETE FROM historial")
        conn.commit()


# ── Blacklist ─────────────────────────────────────────────────────────────────

def agregar_blacklist(device_id: str, patron: str, tipo: str = "palabra"):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO blacklist (device_id, patron, tipo) VALUES (%s, %s, %s)
            """, (device_id, patron.lower().strip(), tipo))
        conn.commit()


def eliminar_blacklist(blacklist_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM blacklist WHERE id = %s", (blacklist_id,))
        conn.commit()


def obtener_blacklist(device_id: str = None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if device_id:
                cur.execute("""
                    SELECT * FROM blacklist
                    WHERE device_id = %s OR device_id = '*'
                    ORDER BY creado DESC
                """, (device_id,))
            else:
                cur.execute("SELECT * FROM blacklist ORDER BY creado DESC")
            rows = cur.fetchall()
            return [dict(r) for r in rows]


def verificar_blacklist(url: str, device_id: str) -> dict:
    """Verifica si una URL está en la blacklist del dispositivo o global."""
    url_lower = url.lower()
    blacklist = obtener_blacklist(device_id)
    for item in blacklist:
        if item["patron"] in url_lower:
            return {"bloqueado": True, "patron": item["patron"], "id": item["id"]}
    return {"bloqueado": False}