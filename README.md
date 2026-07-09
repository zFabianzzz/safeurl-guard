# 🛡️ SafeURL Guard v2.0

Extensión de Chrome/Edge que detecta y bloquea URLs maliciosas en tiempo real usando **Machine Learning (Random Forest)** entrenado con más de 750,000 URLs reales.

> **Backend en producción:** https://safeurl-guard.onrender.com

---

## 📋 ¿Qué hace esta extensión?

- Analiza automáticamente cada URL que visitas
- Bloquea sitios peligrosos antes de que carguen
- Detecta **Phishing**, **Malware** y **Defacement**
- Muestra el nivel de riesgo en tiempo real (0–100%)
- Guarda un historial de todas las URLs analizadas
- Permite analizar URLs manualmente sin tener que visitarlas

---

## 🚀 Instalación rápida — Sin instalar Python

Si solo quieres usar la extensión sin configurar nada, sigue estos pasos:

**1.** Clona o descarga este repositorio

```bash
git clone https://github.com/zFabianzzz/safeurl-guard.git
```

**2.** Abre Chrome y ve a `chrome://extensions/`

**3.** Activa el **Modo desarrollador** (esquina superior derecha)

**4.** Clic en **"Cargar descomprimida"**

**5.** Selecciona la carpeta `extension/` dentro del proyecto

```
safeurl-guard/
└── extension/   ← selecciona esta carpeta
```

**6.** ✅ Listo — la extensión aparece en la barra del navegador y funciona automáticamente

> **Nota:** La primera vez puede tardar hasta 60 segundos en responder. Si el popup dice "Backend offline", espera un momento y navega a cualquier página.

---

## 🔬 Instalación completa — Ejecutar el backend localmente

Sigue esta opción si quieres ver y modificar el código completo funcionando en tu propia máquina.

---

### Requisitos previos

Instala los siguientes programas antes de comenzar:

| Programa | Versión | Enlace |
|---|---|---|
| Python | 3.11.x | https://www.python.org/downloads/release/python-3119/ |
| Git | Cualquiera | https://git-scm.com/downloads |
| Google Chrome | Cualquiera | https://www.google.com/chrome/ |

> ⚠️ Al instalar Python, marca la casilla **"Add Python to PATH"** antes de hacer clic en Install Now.

---

### Paso 1 — Clonar el repositorio

Abre una terminal y ejecuta:

```bash
git clone https://github.com/zFabianzzz/safeurl-guard.git
cd safeurl-guard
```

---

### Paso 2 — Crear el entorno virtual

```bash
cd backend
py -3.11 -m venv venv
```

---

### Paso 3 — Activar el entorno virtual

```bash
venv\Scripts\activate
```

Sabrás que está activado cuando el prompt muestre `(venv)` al inicio:

```
(venv) PS C:\...\safeurl-guard\backend>
```

> Si PowerShell muestra un error de permisos, ejecuta esto primero y vuelve a intentarlo:
> ```bash
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

### Paso 4 — Instalar las dependencias

```bash
pip install -r requirements.txt
```

Esto descarga e instala todas las librerías necesarias. Puede tardar 2–4 minutos.

---

### Paso 5 — Iniciar el servidor

```bash
uvicorn main:app --reload --port 8000
```

Cuando el servidor esté listo verás esto en la terminal:

```
✅ Modelo Random Forest cargado correctamente
   Accuracy: 0.9461
INFO: Uvicorn running on http://127.0.0.1:8000
```

> ⚠️ Mantén esta terminal abierta mientras usas la extensión. Si la cierras, el servidor se apaga y el popup mostrará "Backend offline".

Verifica que funciona abriendo en el navegador:

```
http://localhost:8000
```

Debe mostrar:

```json
{"message": "SafeURL Guard API v2.0 funcionando correctamente"}
```

---

### Paso 6 — Conectar la extensión a tu servidor local

Abre estos dos archivos con cualquier editor de texto (como VS Code o el Bloc de notas):

- `extension/background.js`
- `extension/popup.js`

En ambos archivos, busca esta línea al inicio y cámbiala:

```javascript
// Antes (servidor en la nube):
const API_BASE = "https://safeurl-guard.onrender.com";

// Después (tu servidor local):
const API_BASE = "http://127.0.0.1:8000";
```

Guarda ambos archivos.

---

### Paso 7 — Cargar la extensión en Chrome

1. Abre Chrome y ve a `chrome://extensions/`
2. Activa el **Modo desarrollador** (esquina superior derecha)
3. Clic en **"Cargar descomprimida"**
4. Selecciona la carpeta `extension/` del proyecto
5. ✅ La extensión aparece en la barra del navegador

---

### Paso 8 — Verificar que todo funciona

- Navega a cualquier página — el popup mostrará el nivel de riesgo automáticamente
- El indicador debe mostrar **"Backend online · ML activo"** en verde
- Prueba el tab **"🔍 Manual"** para analizar una URL sin visitarla

---

## 🤖 Modelo de Machine Learning

El modelo fue entrenado con **182,520 URLs** usando Random Forest con 200 árboles.

| Categoría | Descripción | Acción |
|---|---|---|
| ✅ Segura | Sitio legítimo y confiable | Permitido |
| ⚠️ Sospechosa | Características inusuales | Advertencia |
| 🎣 Phishing | Roba credenciales y datos | Bloqueado |
| ☠️ Malware | Distribuye software malicioso | Bloqueado |
| 💀 Defacement | Sitio hackeado o comprometido | Bloqueado |

**Precisión del modelo: 94.61%**

---

## ❓ Preguntas frecuentes

**¿El popup dice "Backend offline", qué hago?**
Si usas la instalación rápida, espera 60 segundos — el servidor se activa automáticamente la primera vez. Si usas el servidor local, verifica que la terminal con `uvicorn` sigue abierta.

**¿Me bloquea un sitio que no es peligroso, qué hago?**
El modelo tiene un 94.61% de precisión, por lo que ocasionalmente puede haber falsos positivos. En la pantalla de bloqueo puedes hacer clic en "Continuar bajo riesgo" para acceder de todas formas.

**¿Funciona en Edge o Brave?**
Sí. En Edge ve a `edge://extensions/` y en Brave ve a `brave://extensions/`. El resto de los pasos es idéntico.

**¿Funciona en Firefox o Safari?**
No. Esta extensión es compatible solo con navegadores basados en Chromium (Chrome, Edge, Brave, Opera).

**¿Necesito internet para que funcione?**
Sí, la extensión necesita conectarse al servidor para analizar las URLs. Sin conexión mostrará "Backend offline".

---

## 📁 Estructura del proyecto

```
safeurl-guard/
├── backend/
│   ├── main.py                  # Servidor FastAPI principal
│   ├── requirements.txt         # Dependencias Python
│   ├── Procfile                 # Configuración para Render
│   ├── merge_and_retrain.py     # Reentrenar con nuevos datos
│   ├── model/
│   │   ├── rf_model.joblib      # Modelo entrenado (Random Forest)
│   │   └── model_metadata.json  # Información del modelo
│   ├── database/
│   │   └── db.py                # Base de datos SQLite
│   └── services/
│       ├── analyzer.py          # Lógica de análisis con ML
│       └── feature_extractor.py # Extrae características de URLs
│
└── extension/
    ├── manifest.json            # Configuración de la extensión
    ├── background.js            # Análisis automático en segundo plano
    ├── popup.html / popup.js    # Interfaz del popup
    ├── blocked.html / blocked.js # Página de bloqueo
    ├── settings.html / settings.js # Página de configuración
    └── icons/                   # Iconos de la extensión
```

---

## 🔧 API — Endpoints disponibles

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Estado general de la API |
| GET | `/health` | Estado del servidor y modelo |
| POST | `/analizar-url` | Analiza una URL |
| GET | `/historial` | Obtiene el historial de análisis |
| DELETE | `/historial` | Elimina todo el historial |
| GET | `/estadisticas` | Estadísticas globales |

Documentación interactiva disponible en: `http://localhost:8000/docs`