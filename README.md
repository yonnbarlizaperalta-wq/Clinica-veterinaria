# Clínica veterinaria Huellitas

Sistema académico en Django para gestionar propietarios, mascotas, historias clínicas, veterinarios, citas, vacunas y sus aplicaciones. Toda la información se administra desde Django Admin en español.

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

Abre <http://127.0.0.1:8000/admin/>. El comando `generar_entregable.ps1` crea tres registros por tabla y el superusuario demo si no existe. Credenciales locales de demostración: **admin / Huellitas2026!**. Cambia esa contraseña antes de usar el sistema fuera de una demostración local. Para elegir otra credencial durante la generación:

```powershell
.\generar_entregable.ps1 -AdminUser miusuario -AdminPassword 'UnaClaveSegura'
```

## Funcionalidades

- Registro y búsqueda de propietarios con sus mascotas dentro del mismo formulario.
- Ficha de mascota con historia clínica (1:1) y aplicaciones de vacunas (entidad intermedia).
- Agenda de citas con veterinario, mascota, estado, fecha y motivo.
- Catálogo de vacunas y seguimiento de dosis, lote y próxima aplicación.
- Filtros, búsqueda, listados y navegación entre registros desde el panel admin.
- Base `db.sqlite3` incluida con registros demo precargados.

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
