
Readme · MD
# 🛡️ SafeURL Guard v2.0
 
Extensión de Chrome que detecta y bloquea URLs maliciosas en tiempo real usando **Machine Learning**.
 
---
 
## ⚡ Opción A — Solo instalar la extensión (sin instalar Python)
 
Esta opción usa el backend ya desplegado en internet. No necesitas instalar nada más que la extensión.
 
**Paso 1** — Descarga o clona este repositorio
 
```bash
git clone https://github.com/zFabianzzz/safeurl-guard.git
```
 
**Paso 2** — Abre Chrome y ve a:
 
```
chrome://extensions/
```
 
**Paso 3** — Activa el **"Modo desarrollador"** (toggle arriba a la derecha)
 
**Paso 4** — Clic en **"Cargar descomprimida"**
 
**Paso 5** — Selecciona la carpeta `extension` que está dentro del proyecto
 
```
safeurl-guard/
└── extension/   ← selecciona esta carpeta
```
 
**Paso 6** — ✅ Listo. La extensión ya aparece en Chrome y funciona automáticamente.
 
> ⚠️ La primera vez puede tardar hasta 60 segundos en responder porque el servidor se activa automáticamente. Si el popup dice "Backend offline", espera un momento y navega a cualquier página.
 
---
 
## 🔬 Opción B — Ejecutar el backend en tu propia PC
 
Usa esta opción si quieres ver el código completo funcionando en tu máquina.
 
### Requisitos
 
Instala estos programas antes de empezar:
 
- **Python 3.11** → https://www.python.org/downloads/release/python-3119/
  - ⚠️ Durante la instalación marca la casilla ☑️ **"Add Python to PATH"**
- **Git** → https://git-scm.com/downloads
---
 
### Paso 1 — Clonar el repositorio
 
```bash
git clone https://github.com/zFabianzzz/safeurl-guard.git
cd safeurl-guard
```
 
---
 
### Paso 2 — Entrar a la carpeta del backend
 
```bash
cd backend
```
 
---
 
### Paso 3 — Crear el entorno virtual
 
```bash
py -3.11 -m venv venv
```
 
---
 
### Paso 4 — Activar el entorno virtual
 
```bash
venv\Scripts\activate
```
 
Sabrás que está activado cuando el prompt muestre `(venv)` al inicio.
 
> Si te da error en PowerShell, ejecuta primero esto y vuelve a intentarlo:
> ```bash
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
 
---
 
### Paso 5 — Instalar las dependencias
 
```bash
pip install -r requirements.txt
```
 
Esto descarga todas las librerías necesarias. Puede tardar 2-3 minutos.
 
---
 
### Paso 6 — Iniciar el servidor
 
```bash
uvicorn main:app --reload --port 8000
```
 
Cuando veas esto en la terminal, el servidor está listo:
 
```
✅ Modelo Random Forest cargado correctamente
   Accuracy: 0.9461
INFO: Uvicorn running on http://127.0.0.1:8000
```
 
> ⚠️ Deja esta terminal abierta mientras usas la extensión. Si la cierras, el servidor se apaga.
 
Verifica que funciona abriendo en el navegador:
**http://localhost:8000**
 
Debe aparecer:
```json
{"message": "SafeURL Guard API v2.0 funcionando correctamente"}
```
 
---
 
### Paso 7 — Cambiar la extensión para usar tu servidor local
 
Abre estos dos archivos en un editor de texto:
 
- `extension/background.js`
- `extension/popup.js`
En ambos archivos busca esta línea al inicio y cámbiala:
 
```javascript
// Antes (servidor en la nube):
const API_BASE = "https://safeurl-guard.onrender.com";
 
// Después (tu servidor local):
const API_BASE = "http://127.0.0.1:8000";
```
 
Guarda ambos archivos.
 
---
 
### Paso 8 — Cargar la extensión en Chrome
 
1. Abre Chrome y ve a `chrome://extensions/`
2. Activa el **"Modo desarrollador"** (toggle arriba a la derecha)
3. Clic en **"Cargar descomprimida"**
4. Selecciona la carpeta `extension/` dentro del proyecto
5. ✅ La extensión aparece en la barra del navegador
---
 
### Paso 9 — Verificar que todo funciona
 
- Navega a cualquier página web — el popup mostrará el análisis automáticamente
- El popup debe mostrar **"Backend online · ML activo"** en verde
- Prueba con una URL sospechosa desde el tab **"🔍 Manual"**
---
 
## ❓ Preguntas frecuentes
 
**¿Por qué el popup dice "Backend offline"?**
- Si usas la Opción A: espera 60 segundos, el servidor se está despertando
- Si usas la Opción B: verifica que la terminal con `uvicorn` sigue abierta
**¿Por qué me bloquea sitios que no son peligrosos?**
- El modelo tiene 94.61% de precisión, por lo que puede tener falsos positivos
- Puedes hacer clic en "Continuar bajo riesgo" para acceder de todas formas
**¿Puedo usar la extensión en Edge?**
- Sí, Edge también soporta extensiones de Chrome. Los pasos son los mismos
**¿El servidor de la nube tiene mis datos?**
- El servidor solo guarda las URLs analizadas para el historial
- No guarda información personal ni credenciales
---
 
## 🌐 Backend en la nube
 
El backend está disponible en:
 
**https://safeurl-guard.onrender.com**
 
| Dirección | Descripción |
|---|---|
| https://safeurl-guard.onrender.com | Estado general |
| https://safeurl-guard.onrender.com/health | Estado del modelo |
| https://safeurl-guard.onrender.com/historial | Historial de análisis |
| https://safeurl-guard.onrender.com/docs | Documentación de la API |
 
---
 
## 📊 Sobre el modelo
 
El modelo fue entrenado con **182,520 URLs** de 4 categorías:
 
| Categoría | Descripción |
|---|---|
| ✅ Segura | Sitios legítimos y confiables |
| 🎣 Phishing | Sitios que roban credenciales |
| ☠️ Malware | Sitios que distribuyen software malicioso |
| 💀 Defacement | Sitios comprometidos o hackeados |
 
**Precisión del modelo: 94.61%**