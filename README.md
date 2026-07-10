# 🛡️ SafeURL Guard

**SafeURL Guard** es una extensión para el navegador Chrome que analiza cada página web que visitas y te avisa si podría ser peligrosa (phishing, malware, sitios falsos, etc.), usando un modelo de Inteligencia Artificial entrenado para reconocer patrones de URLs maliciosas.

Incluye además un **panel de administración** donde se puede ver qué dispositivos están usando la extensión, revisar el historial de sitios analizados, y bloquear manualmente sitios específicos.

---

## 🧪 Guía de instalación local (laboratorio)

Vamos a instalar el proyecto completo en tu computadora usando **Visual Studio Code**. Sigue los pasos exactamente en orden — no te saltes ninguno, aunque parezca obvio.

**No necesitas instalar ninguna base de datos ni configurar nada a mano.** El proyecto crea su propia base de datos local automáticamente la primera vez que lo enciendes.

### ✅ Antes de empezar, necesitas tener instalado:

| Programa | Dónde descargarlo |
|---|---|
| **Python 3.11 o 12** | [python.org/downloads](https://www.python.org/downloads/) |
| **Visual Studio Code** | [code.visualstudio.com](https://code.visualstudio.com/) |
| **Google Chrome** | [google.com/chrome](https://www.google.com/chrome/) |

> ⚠️ **MUY IMPORTANTE (Windows):** al instalar Python, la primera pantalla del instalador tiene una casilla abajo que dice **"Add Python to PATH"** (o "Add python.exe to PATH"). **Actívala antes de darle a "Install Now"**. Si no lo haces, ninguno de los comandos de este manual va a funcionar y vas a tener que desinstalar y volver a instalar Python.

Si ya tienes estos tres programas instalados, puedes saltar directo al Paso 1.

---

### Paso 1 — Descargar el proyecto

1. Entra al repositorio del proyecto en GitHub (el link te lo comparte el instructor).
2. Haz clic en el botón verde que dice **`<> Code`**.
3. Haz clic en **"Download ZIP"**.
4. Ve a tu carpeta de **Descargas**, busca el archivo `.zip` que se descargó.
5. Haz **clic derecho** sobre el archivo → **"Extraer todo..."** → **"Extraer"**.
6. Vas a terminar con una carpeta llamada `safeurl-guard-main` (o similar). **Recuerda en qué carpeta la dejaste**, la vas a necesitar en el siguiente paso.

### Paso 2 — Abrir el proyecto en Visual Studio Code

1. Abre **Visual Studio Code**.
2. Ve al menú de arriba: **Archivo (File) → Abrir carpeta... (Open Folder...)**
3. Busca y selecciona la carpeta `safeurl-guard-main` que descomprimiste en el Paso 1.
4. Haz clic en **"Seleccionar carpeta"**.

Del lado izquierdo (el panel llamado **EXPLORER**) deberías ver las carpetas `backend` y `extension`.

### Paso 3 — Abrir la terminal dentro de VS Code

1. En el menú de arriba de VS Code, haz clic en **Terminal → New Terminal** (o "Ver → Terminal" según tu versión).
2. Se abre un panel abajo con una línea de texto que empieza con `PS C:\Usuarios\...` — ahí es donde vamos a escribir todos los comandos de aquí en adelante.

> 💡 **Nota sobre esta terminal:** en Windows, VS Code abre por defecto una terminal llamada **PowerShell**. Tiene una particularidad: **no se pueden escribir dos comandos juntos separados por `&&`** (a diferencia de otros sistemas). Por eso, en esta guía, cada comando va en su **propia línea** — escribe uno, presiona Enter, espera a que termine, y recién ahí escribe el siguiente. No copies varias líneas de comando pegadas de una sola vez.

### Paso 4 — Entrar a la carpeta del backend

En la terminal que abriste, escribe exactamente esto y presiona **Enter**:

```
cd backend
```

Fíjate que el texto que aparece antes del cursor cambie e incluya `\backend` al final — eso confirma que sí entraste a la carpeta correcta.

### Paso 5 — Crear el ambiente virtual

Escribe este comando y presiona Enter:

```
python -m venv venv
```

No va a mostrar ningún mensaje visible mientras trabaja — espera unos 10-20 segundos hasta que puedas volver a escribir en la terminal. Esto crea una carpeta nueva llamada `venv` (la vas a ver aparecer del lado izquierdo, dentro de `backend`). Es una "caja aislada" donde se instalan las librerías del proyecto sin afectar el resto de tu computadora.

### Paso 6 — Activar el ambiente virtual

Escribe este comando y presiona Enter:

```
venv\Scripts\activate
```

**Verifica que funcionó:** el texto al inicio de la línea de tu terminal debe cambiar y ahora empezar con `(venv)`, por ejemplo:
```
(venv) PS C:\Users\TuNombre\Downloads\safeurl-guard-main\backend>
```

⚠️ Si NO aparece `(venv)` al inicio, **detente aquí** y avísale al instructor antes de seguir — significa que el paso anterior no funcionó.

> Si te sale un error que menciona "execution of scripts is disabled" (ejecución de scripts deshabilitada), es una restricción de seguridad de Windows. Solución: escribe este comando, presiona Enter, escribe `S` (o `Y`) cuando te pregunte, y vuelve a intentar el Paso 6:
> ```
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### Paso 7 — Instalar las librerías necesarias

Con `(venv)` visible al inicio de tu línea, escribe:

```
pip install -r requirements.txt
```

Presiona Enter y **espera** — va a mostrar mucho texto pasando y puede tardar entre 2 y 5 minutos la primera vez, dependiendo de tu conexión a internet. Es normal, no lo interrumpas. Termina cuando vuelves a ver la línea `(venv) PS ...>` lista para escribir de nuevo, sin errores en rojo al final.

### Paso 8 — Encender el backend

Escribe este comando y presiona Enter:

```
uvicorn main:app --reload --port 8000
```

Si todo salió bien, vas a ver estas líneas (entre otras):

```
INFO:main:Base de datos inicializada
INFO: Uvicorn running on http://127.0.0.1:8000
```

Con esto, el sistema ya creó automáticamente su propia base de datos local (no tuviste que instalar ni configurar nada de eso).

🛑 **NO cierres esta terminal.** Este proceso tiene que quedarse corriendo todo el tiempo que uses la extensión — es el "cerebro" que analiza las URLs. Si lo cierras (o presionas `Ctrl+C`), la extensión deja de funcionar hasta que vuelvas a correr este mismo comando.

### Paso 9 — Cargar la extensión en Chrome

Ahora abre **Google Chrome** (déjalo abierto junto a VS Code, no cierres nada):

1. En la barra de direcciones de Chrome, escribe exactamente esto y presiona Enter:
   ```
   chrome://extensions/
   ```
2. Arriba a la derecha vas a ver un interruptor que dice **"Modo de desarrollador"**. Actívalo (debe quedar encendido/azul).
3. Va a aparecer un botón nuevo arriba que dice **"Cargar descomprimida"**. Haz clic ahí.
4. Se abre un explorador de archivos. Navega hasta la carpeta `safeurl-guard-main` que descomprimiste, entra en ella, y selecciona la carpeta **`extension`** (esa carpeta específica, no la carpeta completa del proyecto).
5. Haz clic en **"Seleccionar carpeta"**.

Deberías ver aparecer la tarjeta de **"SafeURL Guard"** en esa página, con un interruptor azul indicando que está activada.

### Paso 10 — ¡Probarlo!

1. Haz clic en el ícono del **rompecabezas 🧩** (arriba a la derecha de Chrome, junto a la barra de direcciones).
2. Busca "SafeURL Guard" en la lista y haz clic en el **📌 (pin)** para que quede siempre visible.
3. Navega a cualquier página web (por ejemplo, `wikipedia.org`).
4. Haz clic en el ícono de SafeURL Guard — deberías ver el resultado del análisis de esa página.

Para ver el panel de administración, abre en Chrome:
```
http://127.0.0.1:8000/admin
```
La contraseña por defecto es: `SafeURL@Admin2024!`

---

## 🔧 Solución de problemas comunes

**Al escribir `python` la terminal dice "no se reconoce como un comando"**
No marcaste "Add Python to PATH" al instalar Python. Vuelve a correr el instalador de Python, elige la opción "Modify" (Modificar), y activa esa casilla.

**Al escribir `pip install -r requirements.txt` salen errores en rojo**
Confirma que `(venv)` aparece al inicio de tu línea de terminal (Paso 6). Si no aparece, el Paso 7 no va a funcionar bien.

**La extensión no analiza nada / dice que no se conecta**
Revisa que la terminal del Paso 8 siga abierta, con el texto `Uvicorn running on...` visible y sin haberla cerrado.

**El panel de administración dice "Unauthorized" o te saca la sesión**
Vuelve a iniciar sesión con la contraseña de administrador — es normal después de un rato sin usarlo.

**Hice cambios en algún archivo de la carpeta `extension/` y no se ven**
Ve a `chrome://extensions/` y haz clic en el botón 🔄 (recargar) sobre la tarjeta de SafeURL Guard.

**Quiero volver a empezar de cero (borrar todos los datos guardados)**
En la terminal del Paso 8, presiona `Ctrl+C` para detener el servidor. Luego busca y borra el archivo `backend/safeurl_local.db` desde el panel EXPLORER de VS Code (clic derecho → Eliminar). Vuelve a correr el comando del Paso 8 — se crea una base de datos nueva y vacía.

**Cerré VS Code / apagué la computadora y quiero volver a usarlo otro día**
No hace falta repetir todos los pasos. Solo:
1. Abre VS Code → Abrir carpeta → la carpeta del proyecto.
2. Abre una terminal nueva (Paso 3).
3. Escribe `cd backend` y Enter.
4. Escribe `venv\Scripts\activate` y Enter.
5. Escribe `uvicorn main:app --reload --port 8000` y Enter.
6. La extensión en Chrome ya sigue instalada de antes, no hay que cargarla de nuevo.

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
