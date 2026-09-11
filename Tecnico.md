# Documentación Técnica — App Web Gestión de Contactos

## 1. Resumen del proyecto

Aplicación web desarrollada en **Python/Flask** para la gestión de contactos personales, organizados mediante un sistema de **etiquetas** (muchos a muchos). Incluye autenticación de usuarios, control de permisos por rol (administrador), carga masiva de contactos desde un export CSV de Google Contacts, y un subsistema independiente de **alertas** (correo, scraping, hoja de cálculo) pensado para ejecutarse en un NAS Synology mediante Docker.

El proyecto parte como adaptación de otro ejemplo (`Appweb Tienda videojuegos`) y está en desarrollo activo (ver bitácora en `README.md`).

No es un repositorio Git (`Is a git repository: false`), por lo que no hay historial de control de versiones asociado.

## 2. Stack tecnológico

| Categoría | Tecnología |
|---|---|
| Lenguaje | Python 3.13 |
| Framework web | Flask 3.1.0 |
| ORM | Flask-SQLAlchemy 3.1.1 (SQLAlchemy Core/ORM) |
| Autenticación | Flask-Login 0.6.3 |
| Formularios | Flask-WTF 1.2.2 / WTForms |
| UI | Flask-Bootstrap 3.3.7.1 (Bootstrap 3, plantillas Jinja2) |
| Base de datos | SQLite |
| Procesamiento de datos | pandas 2.2.3, openpyxl 3.1.5, lxml 5.3.1 |
| Integraciones alertas | gspread 6.2.0 + oauth2client 4.1.3 (Google Sheets), python-dotenv 1.0.1, pip-system-certs |
| Contenedores | Docker / docker-compose (imagen base `python:3.13.2`) |
| Despliegue | NAS Synology (red `host`, proxy inverso `javicu.synology.me:5001`) |

## 3. Estructura del proyecto

```
07_Appweb_contactos/
├── run.py                     # Punto de entrada de la app web
├── ejecutar.sh                # Script de arranque en el contenedor (NAS)
├── alertas.sh                 # Script alternativo solo-alertas
├── docker-compose.yaml        # Definición del servicio Docker
├── requirements.txt           # Dependencias Python
├── requirements.log           # Log de instalación (generado por ejecutar.sh)
├── README.md                  # Bitácora de tareas / referencias
│
├── app/                       # Paquete principal de la aplicación Flask
│   ├── __init__.py            # (vacío)
│   ├── app.py                 # Factoría/instancia de Flask, extensiones y blueprints
│   ├── config.py               # Configuración (SECRET_KEY, DEBUG, URI de BD)
│   │
│   ├── usuarios/               # Blueprint: autenticación y usuarios
│   │   ├── __init__.py
│   │   ├── models.py            # Modelo Usuarios
│   │   ├── forms.py             # LoginForm, formUsuario, formChangePassword
│   │   └── routes.py            # /login, /logout, /registro
│   │
│   ├── contactos/               # Blueprint: gestión de contactos
│   │   ├── __init__.py
│   │   ├── models.py            # Contactos, Rel_contacto_etiqueta
│   │   ├── forms.py             # formContacto, formSINO
│   │   └── routes.py            # CRUD de contactos + carga por archivo
│   │
│   ├── etiquetas/                # Blueprint: gestión de etiquetas
│   │   ├── __init__.py
│   │   ├── models.py             # Etiquetas
│   │   ├── forms.py              # formEtiqueta, formSINO
│   │   └── routes.py             # CRUD de etiquetas
│   │
│   ├── comunes/
│   │   └── utilidades.py         # procesar_archivo(): parseo de export CSV de Google
│   │
│   └── templates/
│       ├── base.html             # Layout base (navbar + jumbotron), extiende bootstrap/base.html
│       ├── contactos/            # contactos.html, contactos_new.html, contactos_delete.html
│       ├── etiquetas/            # etiquetas.html, etiqueta_new.html, etiqueta_delete.html
│       └── usuarios/             # login.html, registro.html, usuarios_new.html
│
└── alertas/                      # Subsistema independiente de alertas (cron-like, vía ejecutar.sh)
    ├── alertas.py                 # Orquestador: importa y ejecuta cada alerta
    ├── alerta_CONTROL.py           # Alerta de "señal de vida" por correo (CONTROL ACCESO)
    ├── alerta_MD.py                # Scraping de ofertas de empleo (Madrid Digital)
    └── alerta_ficheros_sheet.py    # Detecta ficheros grandes en disco y actualiza Google Sheet
```

## 4. Arquitectura de la aplicación

### 4.1 Inicialización (`app/app.py`)

- Se crea una única instancia global `app = Flask(__name__)` (patrón "instancia global", no *application factory*).
- Configuración cargada desde `app/config.py` vía `app.config.from_object(config)`.
- Extensiones inicializadas: `Bootstrap(app)`, `db = SQLAlchemy(app)`, `LoginManager()` (con `login_view = "login"`).
- Se registran tres **Blueprints**: `usuarios_bp`, `contactos_bp`, `etiquetas_bp`.
- **Particularidad**: aunque se definen Blueprints, las rutas dentro de cada `routes.py` están decoradas con `@app.route(...)` (la instancia global `app`, importada desde `app.app`) en lugar de `@<blueprint>.route(...)`. Los blueprints se registran pero, tal como está el código, no aportan namespacing de rutas ni de `url_for` — el efecto práctico es el de módulos de rutas separados por carpetas, más que blueprints Flask "puros".
- `run.py` es el punto de entrada: crea las tablas con `db.create_all()` dentro del contexto de la app y arranca el servidor:
  - En Windows (`os.name == 'nt'`): `aplicacion.run(port=5010)`.
  - En otros sistemas (NAS/Linux): también `aplicacion.run(port=5010)` en HTTP plano (hay código comentado para HTTPS con certificados, sustituido por el uso del proxy inverso del NAS).

### 4.2 Configuración (`app/config.py`)

```python
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'   # ⚠ hardcodeada en el código fuente
DEBUG = True                                     # ⚠ activo también en el path "producción"
SQLALCHEMY_DATABASE_URI = 'sqlite:////usr/bd/sqlite/contactos_07.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

- La ruta de la base de datos SQLite está fijada a la ruta del volumen montado en el NAS (`/usr/bd/sqlite/contactos_07.db`), correspondiente al volumen `/volume1/informatica/Python/bd` definido en `docker-compose.yaml`. No hay una variante para desarrollo local en Windows (hay una alternativa comentada que usaba una carpeta `instancias/`).
- No existe fichero `.env` en el repo para estos valores (aunque `python-dotenv` está entre las dependencias, usado por el subsistema de alertas).

## 5. Modelo de datos

Tablas (SQLite, sin migraciones — se crean con `db.create_all()`):

### `usuarios`
| Campo | Tipo | Notas |
|---|---|---|
| id | Integer PK | |
| username | String(100) | not null |
| password_hash | String(128) | not null; generado con `werkzeug.security.generate_password_hash` |
| nombre | String(200) | not null |
| email | String(200) | not null |
| admin | Boolean | default `False` |

- Propiedad `password` de solo escritura (setter que hashea; el getter lanza `AttributeError`).
- `verify_password()` valida contra el hash.
- Implementa la interfaz de `flask_login` (`is_authenticated`, `is_active`, `is_anonymous`, `get_id`) y un método propio `is_admin()`.

### `contactos`
| Campo | Tipo | Notas |
|---|---|---|
| id | Integer PK | |
| nombre | String(100) | not null |
| apellidos | String(100) | nullable |
| notas | String(255) | |
| rel_etiquetas | relationship → `Rel_contacto_etiqueta` | `cascade="all, delete-orphan"`, `lazy='dynamic'` |

### `etiquetas`
| Campo | Tipo | Notas |
|---|---|---|
| id | Integer PK | |
| nombre | String(100) | |
| descripcion | String(255) | |

### `rel_contacto_etiqueta` (tabla intermedia N:M)
| Campo | Tipo | Notas |
|---|---|---|
| id | Integer PK | |
| EtiquetaId | Integer FK → `etiquetas.id` | not null |
| ContactoId | Integer FK → `contactos.id` | not null |

Relación **Contactos ↔ Etiquetas**: muchos a muchos, materializada explícitamente como tabla de asociación con modelo propio (no `secondary=` de SQLAlchemy), y gestionada manualmente en las rutas (borrado y reinserción de relaciones en cada edición, en vez de usar operaciones de colección ORM).

**Particularidad del negocio**: en varias consultas se excluye la primera etiqueta de la lista (`Etiquetas.query.all()[1:]`), lo que sugiere que la etiqueta con `id=1` se usa como registro "vacío"/placeholder por convención, no por un flag explícito en el modelo.

## 6. Módulos funcionales

### 6.1 `usuarios` — Autenticación

Rutas (todas definidas sobre `app`, sin prefijo de blueprint):

| Ruta | Métodos | Descripción |
|---|---|---|
| `/`, `/login` | GET/POST | Login; redirige a `contactos` si ya autenticado |
| `/logout` | GET | Cierra sesión |
| `/registro` | GET/POST | Alta de usuario nuevo (siempre `admin=False`) |

- `load_user` registrado como `user_loader` de `flask_login`.
- Sin recuperación de contraseña ni verificación de email.
- El formulario `formChangePassword` existe pero no tiene ruta asociada (funcionalidad incompleta).
- No hay ruta implementada para `/perfil/<username>` aunque el navbar (`base.html`) enlaza a ella.

### 6.2 `contactos` — CRUD + carga masiva

| Ruta | Métodos | Auth | Descripción |
|---|---|---|---|
| `/contactos/`, `/contactos/<id>` | GET | login | Lista contactos; si `id` corresponde a una etiqueta, filtra por ella vía la tabla de relación |
| `/contactos/new` | GET/POST | login + admin | Alta de contacto con selección múltiple de etiquetas |
| `/contactos/<id>/edit` | GET/POST | login + admin | Edición; recrea las relaciones etiqueta-contacto desde cero |
| `/contactos/<id>/delete` | GET/POST | login + admin | Borrado con confirmación (`formSINO`) |
| `/subir` | POST | — (⚠ sin `@login_required`) | Carga masiva desde archivo CSV exportado de Google Contacts |

Notas técnicas:
- El control de permisos de administrador se hace por código (`if not current_user.is_admin(): abort(404)`), repetido en cada ruta protegida — no hay decorador reutilizable ni `flask-principal`/roles centralizados.
- `/subir` **no** tiene `@login_required`, a diferencia del resto de rutas de escritura — posible inconsistencia de seguridad.
- La carga por archivo (`subir_archivo`) evita duplicados por `nombre` exacto pero **no actualiza** contactos existentes (confirmado también en la bitácora del README como tarea pendiente).
- Búsqueda de contactos por nombre (`ilike`) está prevista en comentario pero no implementada.

### 6.3 `etiquetas` — CRUD

| Ruta | Métodos | Auth | Descripción |
|---|---|---|---|
| `/etiquetas/` | GET | login | Lista todas las etiquetas |
| `/etiqueta/new`, `/etiqueta/<id>/edit` | GET/POST | login + admin | Alta/edición (comparten vista `etiqueta_edit`) |
| `/etiqueta/<id>/delete` | GET/POST | login + admin | Borrado con confirmación |

### 6.4 `comunes/utilidades.py` — Importador de Google Contacts

`procesar_archivo(archivo)`:
- Lee el CSV con `pandas.read_csv`.
- Recorre fila a fila y columna a columna aplicando tres diccionarios de mapeo manuales:
  - `transf`: columnas de mapeo directo 1:1 (nombre, notas, cumpleaños, etc.).
  - `doble`: columnas "dobles" de Google (`... Label` + `... Value`) que se combinan en una sola clave del contacto (teléfono, email, dirección, web, redes sociales, etc.).
  - `labels`: traduce las etiquetas de tipo de dato de Google (`Work`, `Mobile`, `* Home`, …) a etiquetas internas en español.
  - `etiquetas`: lista cerrada de nombres de etiquetas de "grupo" reconocidas dentro de la columna `Labels` de Google (p. ej. `Madrid Digital`, `Narval`, `Familia`…), usada para asignar las etiquetas de la app.
- Devuelve una lista de diccionarios (uno por contacto) consumida por `contactos.routes.subir_archivo`.
- Es un parser **ad-hoc y frágil**: depende de nombres de columna concretos del export de Google Contacts y de listas hardcodeadas; columnas no reconocidas solo se imprimen por consola (`print`), sin registro persistente ni feedback al usuario.

## 7. Frontend

- Motor de plantillas: **Jinja2** sobre **Flask-Bootstrap** (Bootstrap 3), heredando de `bootstrap/base.html`.
- `base.html` define navbar (enlaces a Contactos/Etiquetas, y Login/Registro o Perfil/Salir según sesión) y un bloque `contenido` que sobreescriben las plantillas hijas.
- No hay JavaScript/CSS propio relevante ni build frontend (no hay `package.json`); todo el estilo depende de Bootstrap 3 servido por Flask-Bootstrap.
- Formularios renderizados manualmente en las plantillas (no se ha revisado el detalle de cada `*_new.html`, pero usan WTForms vía Flask-WTF, lo que aporta protección CSRF automática en los POST).
- Existe un archivo residual `contactos_new copy.html` (copia de trabajo, no referenciada por ninguna ruta).

## 8. Subsistema de alertas (`alertas/`)

Módulo **independiente** de la app web (no comparte modelos ni base de datos), pensado para ejecutarse periódicamente en el NAS junto al arranque de la app. Depende de un paquete externo `Herramientas` (no incluido en este repo; se copia en tiempo de ejecución, ver §9) que expone utilidades de correo (`mail`), scraping (`scraping`), hoja de cálculo (`sheet`) y lectura de variables de entorno (`variables.leer_variables`).

| Script | Función |
|---|---|
| `alertas.py` | Orquestador: carga configuración y ejecuta las tres alertas en secuencia; en Windows añade una cuarta alerta (`alerta_esqui`, no presente en este repo) |
| `alerta_CONTROL.py` | Sistema de "señal de vida": cuenta correos con asunto `CONTROL ACCESO` no leídos/borrados; si se acumulan (>3, >4), envía avisos escalados y, en el caso extremo, un correo con instrucciones personales y un adjunto financiero a una lista de destinatarios |
| `alerta_MD.py` | Hace scraping de la web de la Comunidad de Madrid (Madrid Digital) buscando procesos selectivos abiertos y envía un correo si detecta puestos nuevos |
| `alerta_ficheros_sheet.py` | Recorre un directorio (`D:\` en Windows / `/video` en NAS) buscando ficheros por encima de un umbral de tamaño y actualiza una Google Sheet vía `gspread` |

Consideraciones:
- Contiene **datos personales sensibles hardcodeados en el código** (ruta a un informe financiero personal, mensaje con instrucciones para familiares en caso de emergencia). Esto es contenido de configuración/negocio del propietario, no un patrón a replicar en otros proyectos.
- Las credenciales de correo y destinatarios se obtienen de variables externas (`leer_variables()`), no están en claro en el código (salvo la ruta del adjunto y el propio mensaje).
- Ejecutado de forma síncrona antes de arrancar la app web (ver `ejecutar.sh`), por lo que un fallo o bloqueo en `alertas.py` retrasa el arranque de la aplicación web.

## 9. Ejecución y despliegue

### 9.1 Desarrollo local (Windows)

```powershell
pip install -r requirements.txt
python run.py
```
- Levanta el servidor en `http://localhost:5010` con `debug=True`.
- Requiere una base SQLite accesible en la ruta configurada en `config.py` (actualmente apunta a una ruta absoluta de NAS `/usr/bd/sqlite/...`, que no existe en Windows — para desarrollo local habría que ajustar `SQLALCHEMY_DATABASE_URI`, p. ej. usando la alternativa comentada basada en `instancias/`).

### 9.2 Despliegue en NAS (Docker)

`docker-compose.yaml` define el servicio `python-07-appweb-contactos-alertas`:
- Imagen base: `python:3.13.2` (sin `Dockerfile` propio, se ejecuta directamente sobre la imagen oficial).
- Red: `host` (sin mapeo de puertos explícito).
- Volúmenes montados desde el NAS:
  - `/volume1/informatica/Python` → `/usr/python` (código fuente)
  - `/volume1/informatica/Python/bd` → `/usr/bd` (base de datos SQLite)
  - `/volume1/informatica/Python/config` → `/usr/config` (certificados/config, solo lectura)
  - `/volume2/video` → `/video` (solo lectura, usado por la alerta de ficheros grandes)
- `working_dir: /usr/python`.
- Comando de arranque: `./Proyectos/07_Appweb_contactos/ejecutar.sh`.

`ejecutar.sh` (ejecutado dentro del contenedor):
1. Instala dependencias: `pip install -r requirements.txt > ./requirements.log`.
2. Copia el paquete externo `Herramientas` al `site-packages` de Python 3.13 (`/usr/local/lib/python3.13/site-packages`), dependencia compartida entre varios proyectos del NAS, no versionada dentro de este repo.
3. Ejecuta `alertas/alertas.py`.
4. Ejecuta `run.py` (arranca la app Flask en el puerto 5010).
5. `wait` a que ambos procesos terminen.

El acceso externo se realiza a través del **proxy inverso del NAS Synology** (`javicu.synology.me:5001`), que gestiona el HTTPS; la app Flask interna sirve en HTTP plano por el puerto 5010 (ver comentario en `run.py` sobre el abandono de SSL directo con certificados).

`alertas.sh` es un script alternativo para ejecutar solo el módulo de alertas sin levantar la app web.

## 10. Dependencias (`requirements.txt`)

```
Flask==3.1.0
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-Bootstrap==3.3.7.1
Flask-WTF==1.2.2
pandas==2.2.3
python-dotenv==1.0.1
gspread==6.2.0
oauth2client==4.1.3
openpyxl==3.1.5
lxml==5.3.1
pip-system-certs==5.3
```

No hay dependencias de testing (`pytest`, etc.) ni de linting/formateo declaradas.

## 11. Seguridad, calidad y deuda técnica (observaciones)

- **`SECRET_KEY` hardcodeada** en `config.py` y versionada en el código fuente; debería moverse a variable de entorno/secreto.
- **`DEBUG = True`** fijo, incluido en el path de ejecución del NAS (no hay diferenciación dev/prod vía variables de entorno).
- **`/subir` sin `@login_required`**: cualquiera con acceso a la URL puede insertar contactos vía carga de archivo, a diferencia del resto de operaciones de escritura.
- Control de permisos de administrador duplicado manualmente (`if not current_user.is_admin(): abort(404)`) en cada ruta, en vez de un decorador común — fácil de olvidar en rutas nuevas.
- **Sin migraciones de base de datos** (no hay Alembic/Flask-Migrate): el esquema se crea con `db.create_all()`, que no aplica cambios a tablas ya existentes; cualquier cambio de modelo en producción requiere migración manual.
- Relación contactos↔etiquetas gestionada a mano (borrar todas las filas de relación y reinsertar) en lugar de usar `secondary=` de SQLAlchemy, lo que añade código repetido y riesgo de inconsistencia.
- Carga masiva de contactos no actualiza registros existentes (limitación conocida, reflejada en el README).
- Parser de importación (`utilidades.py`) frágil ante cambios de formato del export de Google Contacts; listas de mapeo (`labels`, `etiquetas`) hardcodeadas y específicas del propietario de los datos.
- Archivo residual `contactos_new copy.html` sin usar.
- `app/__init__.py` vacío (el paquete no expone una factoría de aplicación reutilizable, dificultando tests automatizados).
- Sin suite de tests automatizados en el repo.
- El subsistema de alertas mezcla responsabilidades de negocio muy personales (finanzas, contacto de emergencia) con infraestructura genérica (detección de ficheros grandes, scraping de empleo) en el mismo orquestador.
- No es repositorio Git; no hay trazabilidad de cambios más allá de la bitácora manual en `README.md`.

## 12. Puntos de extensión pendientes (según bitácora README)

- Depurar/optimizar la carga desde fichero CSV de Google.
- Actualizar contactos ya existentes durante la carga desde fichero (actualmente se omiten).
- Completar el tratamiento de etiquetas nuevas encontradas en la carga desde fichero.
