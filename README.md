# SafeURL Guard v2.0 🛡️

Extensión de Chrome/Edge para detectar y bloquear URLs maliciosas usando **Machine Learning (Random Forest)**.

---

## 📁 Estructura del proyecto

```
safeurl-guard/
├── backend/                    # API Python (FastAPI)
│   ├── main.py                 # Servidor principal
│   ├── train_model.py          # Script de entrenamiento del modelo
│   ├── requirements.txt        # Dependencias Python
│   ├── model/                  # Modelo entrenado (.joblib) ← se genera
│   ├── database/
│   │   └── db.py               # SQLite para historial
│   └── services/
│       ├── analyzer.py         # Lógica ML de análisis
│       └── feature_extractor.py # Extrae features de URLs
│
└── extension/                  # Extensión Chrome/Edge
    ├── manifest.json
    ├── background.js            # Service worker (análisis automático)
    ├── popup.html / popup.js    # Popup principal
    ├── blocked.html             # Página de bloqueo
    ├── settings.html            # Configuración
    └── icons/
```

---

## 🚀 Instalación paso a paso

### 1. Preparar el entorno Python

```bash
# Entrar a la carpeta backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Mac/Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Entrenar el modelo Random Forest

```bash
# Con el dataset completo (651k filas, ~5-10 min)
python train_model.py --data ../dataset_with_all_features_v2.csv

# Con muestra reducida (más rápido, suficiente para pruebas)
python train_model.py --data ../dataset_with_all_features_v2.csv --sample 100000
```

El modelo se guarda en `backend/model/rf_model.joblib`.

### 3. Iniciar el backend

```bash
# Desde la carpeta backend/
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verifica que funciona: http://localhost:8000

### 4. Cargar la extensión en Chrome/Edge

1. Abre Chrome → `chrome://extensions/`
2. Activa **"Modo desarrollador"** (esquina superior derecha)
3. Clic en **"Cargar descomprimida"**
4. Selecciona la carpeta `extension/`
5. ¡Listo! El ícono de SafeURL Guard aparecerá en la barra

---

## 🌐 Publicar la extensión para que cualquiera la instale

### Opción A: Chrome Web Store (recomendado)

1. Crea una cuenta en [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
   - Pago único de $5 USD para registrarse como desarrollador
2. Comprime la carpeta `extension/` en un ZIP
3. Sube el ZIP en el dashboard → "Agregar nuevo artículo"
4. Completa descripción, capturas de pantalla, categoría
5. Espera revisión de Google (1-3 días hábiles)
6. Una vez aprobado, cualquier persona puede instalarla con un clic

> ⚠️ **Para la Chrome Web Store, el backend NO puede ser `localhost`.**
> Necesitas un backend en la nube. Ver sección "Despliegue en la nube" abajo.

### Opción B: Instalar sin Chrome Web Store (para compartir con conocidos)

1. Descarga el ZIP de la extensión
2. Descomprime la carpeta `extension/`
3. En Chrome → `chrome://extensions/` → Modo desarrollador
4. "Cargar descomprimida" → seleccionar la carpeta
5. Compartir el ZIP con tus usuarios + instrucciones

---

## ☁️ Despliegue del backend en la nube (para uso público)

Para que la extensión funcione sin que cada usuario tenga que instalar Python localmente,
despliega el backend en un servidor gratuito:

### Opción A: Render.com (gratis, recomendado)

1. Crea cuenta en [render.com](https://render.com)
2. "New Web Service" → conecta tu repositorio GitHub
3. Configura:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `backend`
4. Una vez desplegado, obtienes una URL tipo `https://safeurl-guard-xxx.onrender.com`
5. En `extension/background.js` y `extension/popup.js`, cambia:
   ```js
   const API_BASE = "https://safeurl-guard-xxx.onrender.com"; // tu URL de Render
   ```

### Opción B: Railway.app (gratis con límites)

1. Cuenta en [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub"
3. Selecciona la carpeta `backend`
4. Railway detecta automáticamente FastAPI

### Notas para producción:

- El modelo `.joblib` debe subirse junto con el código, o entrenarlo en el servidor
- El archivo `safeurl.db` (SQLite) se recrea automáticamente
- Para HTTPS (requerido por Chrome Web Store), Render y Railway lo incluyen gratis

---

## 🤖 Dataset y modelo

El modelo fue entrenado con **651,191 URLs** categorizadas:

| Categoría   | Cantidad | Descripción                     |
|-------------|----------|---------------------------------|
| Benign      | 428,209  | URLs seguras y legítimas        |
| Defacement  | 96,457   | Sitios comprometidos/hackeados  |
| Phishing    | 93,933   | Sitios de robo de credenciales  |
| Malware     | 32,520   | Distribución de software malicioso |

### Agregar más datos

Fuentes de datasets adicionales (gratuitas):
- **PhishTank**: https://phishtank.org/developer_info.php — base de datos de phishing
- **URLhaus**: https://urlhaus.abuse.ch/api/ — URLs de malware en tiempo real
- **OpenPhish**: https://openphish.com/feed.txt — feed de phishing activo
- **Kaggle**: buscar "malicious URLs dataset"

Para agregar nuevas URLs al CSV, mantén las mismas columnas y vuelve a ejecutar `train_model.py`.

---

## 🔧 Endpoints de la API

| Endpoint          | Método | Descripción                     |
|-------------------|--------|---------------------------------|
| `/analizar-url`   | POST   | Analiza una URL                 |
| `/historial`      | GET    | Obtiene el historial            |
| `/estadisticas`   | GET    | Estadísticas globales           |
| `/health`         | GET    | Estado del servidor y modelo    |

Documentación interactiva: http://localhost:8000/docs

---

## 📊 Funcionalidades de la extensión

- ✅ Análisis automático de cada página visitada
- 🚨 Bloqueo automático de sitios peligrosos
- ⚠️ Advertencias para sitios sospechosos
- 🎨 Popup con colores dinámicos según nivel de riesgo
- 🔍 Análisis manual de URLs
- 📋 Historial de navegación analizada
- ⚙️ Configuración personalizable (sensibilidad, bloqueo automático)
- 🤖 Indicador de si se usa el modelo ML o modo heurístico
