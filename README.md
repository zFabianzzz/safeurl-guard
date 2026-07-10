# 🛡️ SafeURL Guard

**SafeURL Guard** es una extensión para el navegador Chrome que analiza cada página web que visitas y te avisa si podría ser peligrosa (phishing, malware, sitios falsos, etc.), usando un modelo de Inteligencia Artificial entrenado para reconocer patrones de URLs maliciosas.

Incluye además un **panel de administración** donde se puede ver qué dispositivos están usando la extensión, revisar el historial de sitios analizados, y bloquear manualmente sitios específicos.

---

## 🧪 Guía para el laboratorio (instalación local)

Esta guía es para tener el proyecto completo — extensión + backend + base de datos — corriendo en tu propia computadora, de forma totalmente local. **No necesitas instalar ninguna base de datos ni configurar nada a mano**: el proyecto crea su propia base de datos local automáticamente la primera vez que lo enciendes.

### Lo único que necesitas instalar antes de empezar

| Programa | Para qué sirve | Dónde descargarlo |
|---|---|---|
| **Python 3.11 o más nuevo** | Corre el backend (el "cerebro" que analiza las URLs) | [python.org/downloads](https://www.python.org/downloads/) |
| **Google Chrome** | Para usar la extensión | [google.com/chrome](https://www.google.com/chrome/) |

> 💡 **Windows:** al instalar Python, asegúrate de marcar la casilla que dice **"Add Python to PATH"** (aparece en la primera pantalla del instalador). Es fácil pasarla por alto y sin eso los siguientes pasos no van a funcionar.

Nada más que instalar. No hace falta PostgreSQL, Docker, ni ninguna otra herramienta.

---

### Paso 1 — Descargar el proyecto

1. Entra al repositorio del proyecto en GitHub.
2. Haz clic en el botón verde **"Code"** → **"Download ZIP"**.
3. Busca el archivo ZIP descargado (normalmente en tu carpeta "Descargas") y descomprímelo (clic derecho → "Extraer todo").

Vas a terminar con una carpeta llamada algo como `safeurl-guard-main`.

### Paso 2 — Abrir una terminal en la carpeta del proyecto

- **Windows:** abre la carpeta del proyecto en el explorador de archivos, haz clic en la barra de direcciones de arriba (donde muestra la ruta de la carpeta), escribe `cmd` y presiona Enter. Se abre una terminal ya ubicada ahí.
- **Mac:** abre la app "Terminal", escribe `cd ` (con un espacio al final), arrastra la carpeta del proyecto hacia la ventana de la terminal, y presiona Enter.

### Paso 3 — Instalar las dependencias de Python

Copia y pega estos comandos uno por uno en la terminal, presionando Enter después de cada uno:

```bash
cd backend
python -m venv venv
```

Esto crea un "ambiente virtual" — una caja aislada donde se instalan las librerías del proyecto sin afectar el resto de tu computadora.

Actívalo:

```bash
# Windows:
venv\Scripts\activate

# Mac:
source venv/bin/activate
```

Deberías ver que aparece `(venv)` al inicio de la línea de tu terminal — eso confirma que se activó bien.

Ahora instala todo lo necesario:

```bash
pip install -r requirements.txt
```

Esto puede tardar 2-3 minutos la primera vez. Es normal.

### Paso 4 — Encender el backend

En la misma terminal (con `(venv)` visible al inicio), escribe:

```bash
uvicorn main:app --reload --port 8000
```

Si todo salió bien, vas a ver algo como esto:

```
INFO:main:Base de datos inicializada
INFO: Uvicorn running on http://127.0.0.1:8000
```

**Con esto ya se creó sola** una base de datos local (un archivo llamado `safeurl_local.db` dentro de la carpeta `backend/`) — no tuviste que instalar ni configurar nada.

⚠️ **Deja esta terminal abierta** mientras uses la extensión. Es el "servidor" que analiza las URLs — si la cierras, la extensión deja de funcionar hasta que la vuelvas a encender con el mismo comando.

### Paso 5 — Cargar la extensión en Chrome

1. Abre una pestaña nueva en Chrome y ve a:
   ```
   chrome://extensions/
   ```
2. Activa el interruptor **"Modo de desarrollador"** (arriba a la derecha).
3. Haz clic en **"Cargar descomprimida"**.
4. Selecciona la carpeta **`extension`** dentro del proyecto (no la carpeta completa del proyecto, solo esa subcarpeta).

Deberías ver el ícono de SafeURL Guard 🛡️ aparecer en tu barra de extensiones (puede que tengas que hacer clic en el ícono del rompecabezas 🧩 para verlo).

### Paso 6 — ¡Probarlo!

- Navega a cualquier página web — se analiza automáticamente en segundo plano.
- Haz clic en el ícono de la extensión para ver el resultado del análisis de la página actual.
- Para ver el panel de administración, abre en el navegador:
  ```
  http://127.0.0.1:8000/admin
  ```
  La contraseña por defecto es: `SafeURL@Admin2024!`

---

## 🔧 Solución de problemas comunes

**Al escribir `python` la terminal dice que no lo reconoce**
En Windows, probablemente no marcaste la casilla "Add Python to PATH" al instalar. Vuelve a correr el instalador de Python, elige "Modify", y activa esa opción.

**"No se conecta al servidor" / la extensión no analiza nada**
Revisa que la terminal donde corre `uvicorn` (Paso 4) siga abierta y sin errores. Si la cerraste, ve a esa carpeta de nuevo, activa el `venv` y vuelve a correr el comando.

**El panel de administración dice "Unauthorized" o me saca la sesión**
Simplemente vuelve a iniciar sesión con la contraseña de administrador — es normal después de un rato sin usarlo.

**Cambié algo en la carpeta `extension/` pero no se ve el cambio**
Ve a `chrome://extensions/` y haz clic en el botón de recargar 🔄 sobre la tarjeta de SafeURL Guard. Chrome no detecta cambios de archivos automáticamente.

**Quiero borrar todo y empezar de cero**
Cierra la terminal del backend, borra el archivo `backend/safeurl_local.db`, y vuelve a correr `uvicorn main:app --reload --port 8000` — se crea una base de datos nueva y vacía.

---

## 📁 Estructura del proyecto (para referencia)

```
safeurl-guard/
├── backend/                     # El "cerebro": analiza las URLs y guarda datos
│   ├── main.py                  # Punto de entrada de la API
│   ├── database/db.py           # Conexión y consultas a la base de datos
│   ├── model/                   # Modelo de Machine Learning ya entrenado
│   ├── services/analyzer.py     # Lógica que clasifica si una URL es peligrosa
│   ├── requirements.txt         # Lista de librerías de Python necesarias
│   └── admin_panel.html         # Panel de administración
└── extension/                   # Lo que se instala en el navegador
    ├── background.js            # Analiza cada página que visitas
    ├── popup.html / popup.js    # Ventana que aparece al hacer clic en el ícono
    ├── blocked.html / blocked.js # Pantalla de advertencia para sitios peligrosos
    ├── settings.html / settings.js
    └── manifest.json            # Configuración de la extensión
```