# Clínica veterinaria Huellitas

Sistema académico en Django para gestionar propietarios, mascotas, historias clínicas, veterinarios, citas, vacunas y sus aplicaciones. Toda la información se administra desde Django Admin en español.

El sitio público está en <http://127.0.0.1:8000/> y el panel para el personal en <http://127.0.0.1:8000/admin/>.

## Requisitos

- Python 3.10 o superior.
- Windows PowerShell (los comandos de abajo usan `.venv\Scripts\python.exe`).

## Instalación y ejecución

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\generar_entregable.ps1
.\.venv\Scripts\python.exe manage.py runserver
```

### VS Code: Django no se puede resolver

Si Pylance subraya `django` con el aviso `could not be resolved from source`, selecciona **Python: Select Interpreter** desde la paleta de comandos (`Ctrl+Shift+P`) y elige `.venv\Scripts\python.exe`. Este proyecto incluye una preferencia de intérprete para esa ruta. Si el entorno aún no tiene dependencias, abre una terminal en la carpeta del proyecto y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py check
```

Después selecciona el intérprete del entorno o reinicia Pylance con **Python: Restart Language Server**. El aviso del editor es de análisis estático; se corrige cuando VS Code usa el entorno que contiene Django.

Abre <http://127.0.0.1:8000/admin/>. El comando `generar_entregable.ps1` prepara las migraciones, los datos demo y el superusuario local. No crea citas de muestra: el calendario queda vacío hasta que alguien registre una cita. Credenciales locales de demostración: **admin / Huellitas2026!**. Cambia esa contraseña antes de usar el sistema fuera de una demostración local. Para elegir otra credencial durante la generación:

```powershell
.\generar_entregable.ps1 -AdminUser miusuario -AdminPassword 'UnaClaveSegura'
```

Cuentas demo del portal del personal: **recepcionista@demo.local / Recepcion2026!** y **veterinario@demo.local / Veterinario2026!**. Ambos ingresan por “Acceso clientes y equipo”; recepción agenda y consulta citas, mientras veterinaria atiende solo las citas asignadas a su ficha y registra las vacunas aplicadas. El administrador crea cuentas de personal desde Administración → Usuarios y las agrega al grupo correspondiente; para veterinarios, también selecciona esa cuenta en Administración → Veterinarios. Los propietarios crean su cuenta desde “Crear cuenta” y solo consultan sus mascotas, citas e historias clínicas.

## Funcionalidades

- Registro y búsqueda de propietarios con sus mascotas dentro del mismo formulario.
- Ficha de mascota con historia clínica (1:1) y aplicaciones de vacunas (entidad intermedia).
- Agenda de citas con veterinario, mascota, estado, fecha y motivo.
- Portada pública de la clínica con servicios, equipo veterinario y resumen de actividad.
- Agenda para recepción y veterinaria: programar citas, completar consultas y registrar vacunas desde el portal.
- Catálogo de vacunas y seguimiento de dosis, lote y próxima aplicación.
- Filtros, búsqueda, listados y navegación entre registros desde el panel admin.
- Grupos de permisos `Recepcionista` y `Veterinario`, además del superusuario administrador.
- Base SQLite local creada por migraciones; cada instalación tiene su propio archivo `db.sqlite3`, excluido del repositorio para proteger los datos registrados.

## Modelo de datos

Siete tablas normalizadas: `tbl_propietario`, `tbl_mascota`, `tbl_historia_clinica`, `tbl_veterinario`, `tbl_cita`, `tbl_vacuna` y `tbl_aplicacion_vacuna`. La última resuelve la relación N:M Mascota–Vacuna y guarda fecha, dosis, lote y próxima fecha. Cada entidad tiene su propia aplicación Django; la tabla intermedia también.

Diagramas: [casos de uso](docs/diagrama_actores.pdf) y [entidad-relación](docs/diagrama_er.pdf).

## Apps

| App | Entidad |
|---|---|
| `propietarios_core` | Propietario |
| `mascotas` | Mascota |
| `historias_clinicas` | Historia clínica |
| `veterinarios` | Veterinario |
| `citas` | Cita |
| `vacunas` | Vacuna |
| `aplicaciones_vacuna` | Aplicación de vacuna (intermedia) |

## Entorno

La base usa SQLite para que el proyecto arranque sin servicios externos. `requirements.txt` fija las dependencias. Las migraciones se incluyen en cada app. Para regenerar la base desde cero, elimina `db.sqlite3` y ejecuta `generar_entregable.ps1`.

Los datos personales del repositorio son ficticios y se usan solo para demostración académica.
