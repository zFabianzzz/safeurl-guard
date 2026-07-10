# 🛡️ SafeURL Guard

**SafeURL Guard** es una extensión para el navegador Chrome que analiza cada página web que visitas y te avisa si podría ser peligrosa (phishing, malware, sitios falsos, etc.), usando un modelo de Inteligencia Artificial entrenado para reconocer patrones de URLs maliciosas.

Incluye además un **panel de administración** donde se puede ver qué dispositivos están usando la extensión, revisar el historial de sitios analizados, y bloquear manualmente sitios específicos.

Hay dos formas de tener la extensión funcionando. Elige la que corresponda a lo que necesitas:

- **[Opción A](#-opción-a--solo-instalar-la-extensión-forma-más-rápida)** — Solo instalar la extensión en tu navegador, usando el servidor que ya está en línea. No necesitas instalar Python ni nada técnico. **Recomendado si solo quieres usarla o probarla.**
- **[Opción B](#-opción-b--instalación-completa-en-tu-computadora-laboratorio)** — Instalar el proyecto completo (extensión + backend + base de datos) en tu propia computadora. Es la guía que seguimos en el laboratorio, pensada para quienes van a explorar o modificar el código.

---

## 📌 Opción A — Solo instalar la extensión (forma más rápida)

Con esta opción, la extensión se conecta automáticamente al servidor que ya está funcionando en internet (desplegado en Render). No instalas Python, ni bases de datos, ni nada técnico — solo cargas una carpeta en Chrome.

### Lo que necesitas
- Tener instalado Google Chrome (o Edge, Brave, u otro navegador basado en Chromium).
- Nada más.

### Paso 1 — Descargar el proyecto

1. Entra al repositorio del proyecto en GitHub.
2. Haz clic en el botón verde **`<> Code`**.
3. Haz clic en **"Download ZIP"**.
4. Ve a tu carpeta de **Descargas**, busca el archivo `.zip`, y haz clic derecho → **"Extraer todo..."** → **"Extraer"**.

Vas a terminar con una carpeta llamada `safeurl-guard-main` (o similar).

### Paso 2 — Abrir la página de extensiones de Chrome

En la barra de direcciones de Chrome, escribe:
```
chrome://extensions/
```

### Paso 3 — Activar el "Modo de desarrollador"

Arriba a la derecha de esa página hay un interruptor que dice **"Modo de desarrollador"**. Actívalo.

### Paso 4 — Cargar la extensión

1. Haz clic en el botón **"Cargar descomprimida"** que aparece arriba.
2. Navega hasta la carpeta `safeurl-guard-main` que descomprimiste, entra en ella, y selecciona la carpeta **`extension`** (esa carpeta específica, no todo el proyecto).
3. Haz clic en **"Seleccionar carpeta"**.

### Paso 5 — ¡Listo!

Debería aparecer el ícono de SafeURL Guard 🛡️ en la barra de extensiones de Chrome (haz clic en el ícono del rompecabezas 🧩 si no lo ves de inmediato). A partir de ahora, cada página que visites se analiza automáticamente usando el servidor en línea.

Para ver el panel de administración:
```
https://safeurl-guard.onrender.com/admin
```
La contraseña de administrador te la va a dar el instructor.

> ⏳ **Nota:** el servidor gratuito "se duerme" cuando nadie lo usa por un rato, así que la primera vez que analices una URL después de un tiempo sin usar la extensión puede tardar entre 30 y 60 segundos en responder. Es normal.

---

## 🧪 Opción B — Instalación completa en tu computadora (laboratorio)

Vamos a instalar el proyecto completo en tu computadora usando **Visual Studio Code**. Sigue los pasos exactamente en orden — no te saltes ninguno, aunque parezca obvio.

**No necesitas instalar ninguna base de datos ni configurar nada a mano.** El proyecto crea su propia base de datos local automáticamente la primera vez que lo enciendes. **Tampoco necesitas instalar Python por separado antes de empezar** — lo vamos a instalar en el Paso 4, directo desde la terminal de VS Code.

### ✅ Antes de empezar, necesitas tener instalado:

- **Visual Studio Code** — [code.visualstudio.com](https://code.visualstudio.com/)
- **Google Chrome** — [google.com/chrome](https://www.google.com/chrome/)

Si ya tienes estos dos programas instalados, puedes saltar directo al Paso 1.

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

### Paso 4 — Instalar Python 3.12 desde la misma terminal

En la terminal que acabas de abrir, escribe este comando y presiona **Enter**:

```
winget install Python.Python.3.12
```

Si te pregunta para aceptar los términos de uso (aparece algo como `[Y/n]`), escribe `Y` y presiona Enter. Espera a que termine — puede tardar 1-2 minutos.

⚠️ **Importante:** cuando termine, **cierra esta terminal y abre una nueva** (haz clic en el ícono 🗑️ para cerrarla, y luego **Terminal → New Terminal**). Esto es necesario para que Windows reconozca el comando de Python recién instalado.

En la terminal nueva, verifica que se instaló correctamente:

```
py -3.12 --version
```

Debe mostrarte algo como `Python 3.12.x`.

> 💡 Usamos específicamente **Python 3.12** (y no la versión "más nueva" disponible) a propósito: algunas librerías del proyecto, como la que conecta con la base de datos, todavía no son totalmente compatibles con versiones muy recientes de Python (como 3.13 o 3.14). Instalarlo así desde el inicio evita ese problema por completo.
>
> Si tu computadora no reconoce el comando `winget` (pasa en algunas versiones viejas de Windows), descarga Python 3.12 manualmente desde [python.org/downloads/release/python-3120](https://www.python.org/downloads/release/python-3120/) — recuerda marcar la casilla **"Add Python to PATH"** durante la instalación.

### Paso 5 — Entrar a la carpeta del backend

En la terminal, escribe exactamente esto y presiona **Enter**:

```
cd backend
```

Fíjate que el texto que aparece antes del cursor cambie e incluya `\backend` al final — eso confirma que sí entraste a la carpeta correcta.

### Paso 6 — Crear el ambiente virtual

Escribe este comando y presiona Enter:

```
py -3.12 -m venv venv
```

No va a mostrar ningún mensaje visible mientras trabaja — espera unos 10-20 segundos hasta que puedas volver a escribir en la terminal. Esto crea una carpeta nueva llamada `venv` (la vas a ver aparecer del lado izquierdo, dentro de `backend`). Es una "caja aislada" donde se instalan las librerías del proyecto sin afectar el resto de tu computadora, usando específicamente la versión de Python que instalamos en el Paso 4.

### Paso 7 — Activar el ambiente virtual

Escribe este comando y presiona Enter:

```
venv\Scripts\activate
```

**Verifica que funcionó:** el texto al inicio de la línea de tu terminal debe cambiar y ahora empezar con `(venv)`, por ejemplo:
```
(venv) PS C:\Users\TuNombre\Downloads\safeurl-guard-main\backend>
```

⚠️ Si NO aparece `(venv)` al inicio, **detente aquí** y avísale al instructor antes de seguir — significa que el paso anterior no funcionó.

> Si te sale un error que menciona "execution of scripts is disabled" (ejecución de scripts deshabilitada), es una restricción de seguridad de Windows. Solución: escribe este comando, presiona Enter, escribe `S` (o `Y`) cuando te pregunte, y vuelve a intentar el Paso 7:
> ```
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### Paso 8 — Instalar las librerías necesarias

Con `(venv)` visible al inicio de tu línea, escribe:

```
python -m pip install -r requirements.txt
```

Presiona Enter y **espera** — va a mostrar mucho texto pasando y puede tardar entre 2 y 5 minutos la primera vez, dependiendo de tu conexión a internet. Es normal, no lo interrumpas. Termina cuando vuelves a ver la línea `(venv) PS ...>` lista para escribir de nuevo, sin errores en rojo al final.

> 💡 Como ya instalamos específicamente Python 3.12 en el Paso 4, este paso no debería dar el error de compatibilidad con `psycopg2-binary`. Si de todas formas te aparece, revisa la sección **"Problemas de compatibilidad con versiones nuevas de Python"** al final de esta guía.

### Paso 9 — Encender el backend

Escribe este comando y presiona Enter:

```
python -m uvicorn main:app --reload --port 8000
```

Si todo salió bien, vas a ver estas líneas (entre otras):

```
INFO:main:Base de datos inicializada
INFO: Uvicorn running on http://127.0.0.1:8000
```

Con esto, el sistema ya creó automáticamente su propia base de datos local (no tuviste que instalar ni configurar nada de eso).

🛑 **NO cierres esta terminal.** Este proceso tiene que quedarse corriendo todo el tiempo que uses la extensión — es el "cerebro" que analiza las URLs. Si lo cierras (o presionas `Ctrl+C`), la extensión deja de funcionar hasta que vuelvas a correr este mismo comando.

### Paso 10 — Cargar la extensión en Chrome

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

### Paso 11 — ¡Probarlo!

1. Haz clic en el ícono del **rompecabezas 🧩** (arriba a la derecha de Chrome, junto a la barra de direcciones).
2. Busca "SafeURL Guard" en la lista y haz clic en el **📌 (pin)** para que quede siempre visible.
3. Navega a cualquier página web (por ejemplo, `wikipedia.org`).
4. Haz clic en el ícono de SafeURL Guard — deberías ver el resultado del análisis de esa página.

Para ver el panel de administración, abre en Chrome:
```
http://127.0.0.1:8000/admin
```
La contraseña de administrador te la va a dar el instructor durante el laboratorio.

---

## 🔧 Solución de problemas comunes (Opción B)

> 💡 **Nota:** esta sección es solo para **consultar si algo falla** durante la instalación completa (Opción B). No es parte de los pasos normales — si todo te salió bien siguiendo la guía de arriba, puedes ignorarla por completo. Si estás con la Opción A (solo la extensión), estos pasos no aplican para ti.

### Problemas generales

**Al escribir `python` o `py -3.12` la terminal dice "no se reconoce como un comando"**
Probablemente el Paso 4 (`winget install Python.Python.3.12`) no terminó de instalar, o no cerraste y volviste a abrir la terminal después de instalarlo (es un paso obligatorio, Windows no reconoce el comando nuevo hasta que abres una terminal nueva). Cierra la terminal actual, abre una nueva, y prueba `py -3.12 --version` de nuevo. Si instalaste Python manualmente desde python.org en vez de con winget, asegúrate de haber marcado "Add Python to PATH" durante la instalación.

**Al escribir `pip install -r requirements.txt` (o `python -m pip install -r requirements.txt`) salen errores en rojo**
Confirma que `(venv)` aparece al inicio de tu línea de terminal (Paso 7). Si no aparece, el Paso 8 no va a funcionar bien. Si el error específico menciona `psycopg2-binary` o `pg_config`, revisa la sección de abajo — es un problema conocido de compatibilidad con versiones nuevas de Python.

**La extensión no analiza nada / dice que no se conecta**
Revisa que la terminal del Paso 9 siga abierta, con el texto `Uvicorn running on...` visible y sin haberla cerrado. También puedes comprobar que el servidor responde abriendo `http://127.0.0.1:8000/admin` directo en Chrome — si esa página no carga, el backend no está corriendo.

**El panel de administración dice "Unauthorized" o te saca la sesión**
Vuelve a iniciar sesión con la contraseña de administrador — es normal después de un rato sin usarlo.

**Hice cambios en algún archivo de la carpeta `extension/` y no se ven**
Ve a `chrome://extensions/` y haz clic en el botón 🔄 (recargar) sobre la tarjeta de SafeURL Guard.

**Quiero volver a empezar de cero (borrar todos los datos guardados)**
En la terminal del Paso 9, presiona `Ctrl+C` para detener el servidor. Luego busca y borra el archivo `backend/safeurl_local.db` desde el panel EXPLORER de VS Code (clic derecho → Eliminar). Vuelve a correr el comando del Paso 9 — se crea una base de datos nueva y vacía.

**Cerré VS Code / apagué la computadora y quiero volver a usarlo otro día**
No hace falta repetir todos los pasos. Solo:
1. Abre VS Code → Abrir carpeta → la carpeta del proyecto.
2. Abre una terminal nueva (Paso 3).
3. Escribe `cd backend` y Enter.
4. Escribe `venv\Scripts\activate` y Enter.
5. Escribe `python -m uvicorn main:app --reload --port 8000` y Enter.
6. La extensión en Chrome ya sigue instalada de antes, no hay que cargarla de nuevo.

---

### Problemas de compatibilidad con versiones nuevas de Python

Esta guía ya instala Python 3.12 específicamente en el Paso 4, así que no deberías toparte con esto. Pero si en algún momento usaste otra versión de Python que ya tenías instalada de antes (por ejemplo, si te saltaste el Paso 4 porque creíste que ya tenías Python), algunas librerías del proyecto — sobre todo `psycopg2-binary`, la que conecta con la base de datos — pueden no ser compatibles todavía con versiones muy nuevas de Python (como 3.13 o 3.14). Esto **no significa que hiciste algo mal**, es una limitación de esas librerías, no del proyecto ni de tus pasos.

**Cómo saber si te está pasando esto:** al correr `pip install -r requirements.txt`, aparece un error parecido a:
```text
Error: pg_config executable not found
ERROR: Failed to build 'psycopg2-binary'
```

**La solución es usar Python 3.12 específicamente para este proyecto** (no hace falta desinstalar la versión que ya tenías — se pueden tener varias versiones de Python instaladas a la vez sin que se estorben entre sí).

**Paso 1 — Desactiva y elimina el entorno virtual actual**

Dentro de la carpeta `backend` (verifica que la ruta de tu terminal termine en `\backend`, si no, escribe `cd backend` primero):

```powershell
deactivate
```
```powershell
Remove-Item -Recurse -Force venv
```

> Si te sale un error como *"No se encuentra la ruta de acceso porque no existe"*, seguramente no estás dentro de la carpeta `backend` — escribe `cd backend` y vuelve a intentar.

**Paso 2 — Instala Python 3.12 si no lo tienes**

Descárgalo desde [python.org/downloads/release/python-3120](https://www.python.org/downloads/release/python-3120/) (recuerda marcar "Add Python to PATH" durante la instalación).

**Paso 3 — Crea un entorno virtual nuevo usando específicamente Python 3.12**

```powershell
py -3.12 -m venv venv
```

Actívalo:
```powershell
venv\Scripts\activate
```

Confirma que quedó en la versión correcta:
```powershell
python --version
```
Debe mostrar algo como `Python 3.12.x` (no 3.14).

**Paso 4 — Instala las dependencias de nuevo**

```powershell
python -m pip install -r requirements.txt
```

**Paso 5 — Inicia el servidor usando `python -m uvicorn` en vez de `uvicorn` a secas**

```powershell
python -m uvicorn main:app --reload --port 8000
```

> Usar `python -m uvicorn` en vez de solo `uvicorn` asegura que se use la versión instalada dentro de tu entorno virtual (`venv`), evitando confusiones si tu computadora tiene otra instalación de Uvicorn por fuera.

---

#### Otros errores relacionados a este cambio de versión

**`py install 3.12` da el error "The 'install' command is unavailable because this is the legacy py.exe command"**
Significa que tu computadora tiene instalado el antiguo "Python Launcher", que no soporta ese comando. Para solucionarlo:
1. Abre la Configuración de Windows → Aplicaciones instaladas.
2. Busca **"Python Launcher"** y desinstálalo (ojo: solo ese, no desinstales "Python Install Manager" ni ninguna versión de Python).
3. Cierra y vuelve a abrir Visual Studio Code, y abre una terminal nueva.
4. Vuelve a intentar `py install 3.12`, y confirma con `py -3.12 --version`.

**Error `Fatal error in launcher: Unable to create process` al correr uvicorn**
Pasa cuando la carpeta del proyecto fue movida, renombrada o copiada después de haber creado el `venv` (el entorno virtual guarda internamente la ruta exacta donde fue creado, y si esa ruta cambia, se rompe). La solución es eliminar el `venv` y crear uno nuevo en la ubicación actual, siguiendo los Pasos 1, 3 y 4 de arriba.

**La instalación parece "trabada" en `Installing collected packages...`**
Es normal — el proyecto usa librerías pesadas (NumPy, Pandas, Scikit-learn, entre otras) que tardan varios minutos en instalarse la primera vez. No cierres la terminal ni presiones `Ctrl+C`. Sabes que terminó bien cuando ves `Successfully installed ...` y vuelve a aparecer el prompt `(venv) PS C:\...>`.

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