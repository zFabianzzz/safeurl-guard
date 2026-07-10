"""
db.py - Base de datos SQLite para SafeURL Guard con soporte multi-dispositivo y panel admin
"""
import sqlite3
import os
import hashlib
import secrets

DB_PATH = os.path.join(os.path.dirname(__file__), "safeurl.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        # Historial por dispositivo
        conn.execute("""
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
        # Dispositivos registrados
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dispositivos (
                device_id TEXT PRIMARY KEY,
                nombre TEXT,
                primera_vez TEXT DEFAULT (datetime('now','localtime')),
                ultima_vez TEXT DEFAULT (datetime('now','localtime')),
                total_urls INTEGER DEFAULT 0
            )
        """)
        # Blacklist por dispositivo (o global con device_id='*')
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                patron TEXT NOT NULL,
                tipo TEXT DEFAULT 'palabra',
                creado TEXT DEFAULT (datetime('now','localtime'))
            )
        """)
        # Admin tokens de sesión
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admin_sessions (
                token TEXT PRIMARY KEY,
                creado TEXT DEFAULT (datetime('now','localtime')),
                expira TEXT
            )
        """)
        conn.commit()
        _crear_admin_por_defecto()


def _crear_admin_por_defecto():
    """Crea la contraseña de admin si no existe en el archivo .env o variable de entorno."""
    pass


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verificar_admin(password: str) -> bool:
    import os
    admin_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")
    if not admin_hash:
        # Si no hay variable de entorno, usar contraseña por defecto hasheada
        default_hash = hash_password("SafeURL@Admin2024!")
        return hash_password(password) == default_hash
    return hash_password(password) == admin_hash


def crear_sesion() -> str:
    token = secrets.token_urlsafe(32)
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO admin_sessions (token, expira)
            VALUES (?, datetime('now', '+8 hours'))
        """, (token,))
        conn.commit()
    return token


def verificar_sesion(token: str) -> bool:
    with get_connection() as conn:
        row = conn.execute("""
            SELECT token FROM admin_sessions
            WHERE token = ? AND expira > datetime('now')
        """, (token,)).fetchone()
        return row is not None


def cerrar_sesion(token: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM admin_sessions WHERE token = ?", (token,))
        conn.commit()


# ── Dispositivos ──────────────────────────────────────────────────────────────

def registrar_dispositivo(device_id: str):
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT device_id FROM dispositivos WHERE device_id = ?", (device_id,)
        ).fetchone()
        if existing:
            conn.execute("""
                UPDATE dispositivos SET ultima_vez = datetime('now','localtime')
                WHERE device_id = ?
            """, (device_id,))
        else:
            conn.execute(
                "INSERT INTO dispositivos (device_id) VALUES (?)", (device_id,)
            )
        conn.commit()


def obtener_dispositivos():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT d.*, COUNT(h.id) as total_urls
            FROM dispositivos d
            LEFT JOIN historial h ON d.device_id = h.device_id
            GROUP BY d.device_id
            ORDER BY d.ultima_vez DESC
        """).fetchall()
        return [dict(r) for r in rows]


# ── Historial ─────────────────────────────────────────────────────────────────

def guardar_analisis(data: dict, device_id: str = "unknown"):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO historial (device_id, url, dominio, clasificacion, riesgo, accion, modelo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            device_id,
            data.get("url", ""),
            data.get("dominio", ""),
            data.get("clasificacion", ""),
            data.get("riesgo", 0),
            data.get("accion", ""),
            data.get("modelo", ""),
        ))
        conn.execute("""
            UPDATE dispositivos SET ultima_vez = datetime('now','localtime'),
            total_urls = total_urls + 1
            WHERE device_id = ?
        """, (device_id,))
        conn.commit()


def obtener_historial(device_id: str = None, limit: int = 100):
    with get_connection() as conn:
        if device_id:
            rows = conn.execute("""
                SELECT * FROM historial WHERE device_id = ?
                ORDER BY fecha DESC LIMIT ?
            """, (device_id, limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM historial ORDER BY fecha DESC LIMIT ?
            """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def obtener_estadisticas():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM historial").fetchone()["c"]
        bloqueadas = conn.execute(
            "SELECT COUNT(*) as c FROM historial WHERE accion='Bloqueado'"
        ).fetchone()["c"]
        dispositivos = conn.execute(
            "SELECT COUNT(*) as c FROM dispositivos"
        ).fetchone()["c"]
        por_tipo = conn.execute("""
            SELECT clasificacion, COUNT(*) as total
            FROM historial GROUP BY clasificacion
        """).fetchall()
        return {
            "total": total,
            "bloqueadas": bloqueadas,
            "dispositivos": dispositivos,
            "por_tipo": [dict(r) for r in por_tipo],
        }


def limpiar_historial(device_id: str = None):
    with get_connection() as conn:
        if device_id:
            conn.execute("DELETE FROM historial WHERE device_id = ?", (device_id,))
        else:
            conn.execute("DELETE FROM historial")
        conn.commit()


# ── Blacklist ─────────────────────────────────────────────────────────────────

def agregar_blacklist(device_id: str, patron: str, tipo: str = "palabra"):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO blacklist (device_id, patron, tipo) VALUES (?, ?, ?)
        """, (device_id, patron.lower().strip(), tipo))
        conn.commit()


def eliminar_blacklist(blacklist_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM blacklist WHERE id = ?", (blacklist_id,))
        conn.commit()


def obtener_blacklist(device_id: str = None):
    with get_connection() as conn:
        if device_id:
            rows = conn.execute("""
                SELECT * FROM blacklist
                WHERE device_id = ? OR device_id = '*'
                ORDER BY creado DESC
            """, (device_id,)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM blacklist ORDER BY creado DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def verificar_blacklist(url: str, device_id: str) -> dict:
    """Verifica si una URL está en la blacklist del dispositivo o global."""
    url_lower = url.lower()
    blacklist = obtener_blacklist(device_id)
    for item in blacklist:
        if item["patron"] in url_lower:
            return {"bloqueado": True, "patron": item["patron"], "id": item["id"]}
    return {"bloqueado": False}