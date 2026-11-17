# Clínica veterinaria Huellitas

## Descripción

Sistema web académico para una clínica veterinaria. Permite a los propietarios registrar sus mascotas, solicitar citas y consultar sus datos. Recepción organiza la agenda; cada veterinario puede consultar y atender las citas asociadas a su ficha. El administrador gestiona usuarios y registros desde Django Admin.

El proceso principal de este corte es la gestión de citas desde una interfaz propia: listar, consultar, crear, editar y eliminar con confirmación.

## Integrantes

- Yonn Barliza
- Luis José López (`@ljlf22`)
- Yair Ospino (`@yirjo`)

## Tecnologías

- Python 3.10 o superior.
- Django 5.2.8.
- SQLite.
- Bootstrap 5.3.3 por CDN en `templates/base.html`; no requiere otro paquete de Python.

## Tablas principales

| Tabla | Descripción |
| --- | --- |
| `tbl_propietario` | Datos personales y vínculo opcional con una cuenta Django. |
| `tbl_mascota` | Paciente y propietario responsable. |
| `tbl_historia_clinica` | Historia clínica principal de una mascota. |
| `tbl_veterinario` | Datos profesionales y cuenta asignada del veterinario. |
| `tbl_cita` | Fecha, motivo, estado, mascota y veterinario. |
| `tbl_vacuna` | Catálogo de vacunas. |
| `tbl_aplicacion_vacuna` | Vacuna aplicada, fecha, dosis, lote, mascota y veterinario. |

Las tablas usan el prefijo `tbl_`; las columnas de llave primaria usan `pk_` y las foráneas `fk_`. Django también crea tablas internas para usuarios, grupos y permisos.

## Diagramas

- Casos de uso: [docs/diagrama_actores.png](docs/diagrama_actores.png)
- Entidad-relación: [docs/diagrama_er.png](docs/diagrama_er.png)

## Funcionalidades

- **CRUD de citas:** listado en `/citas/`; alta en `/citas/nueva/`; detalle en `/citas/<id>/`; edición en `/citas/<id>/editar/`; eliminación con confirmación en `/citas/<id>/eliminar/`.
- La cita relaciona `Mascota` y `Veterinario`; desde la mascota se identifica a su propietario. El formulario impide asignar al mismo veterinario dos citas activas en la misma fecha y hora.
- Administrador y recepcionista pueden completar el CRUD. El veterinario consulta y edita las citas asignadas a su ficha; solo recepción o administración pueden crear o eliminar.
- Las páginas del proceso extienden `templates/base.html`, usan la paleta común y componentes de Bootstrap. Sus plantillas están en `templates/citas/` y sus rutas en `citas/urls.py`.
- El portal de propietarios permite solicitar citas, consultar el calendario y revisar historias clínicas y vacunas propias. El calendario muestra únicamente citas guardadas.
- Django Admin continúa disponible en `/admin/`.

## Estructura del proyecto

```text
config/                  configuración, vistas generales y rutas del sitio
citas/                   modelo, formulario, vistas y rutas del CRUD
propietarios_core/        propietarios
mascotas/                 mascotas
historias_clinicas/       historias clínicas
veterinarios/             veterinarios y vínculo a su cuenta
vacunas/                  catálogo de vacunas
aplicaciones_vacuna/      aplicaciones de vacunas y datos demo
templates/base.html       base Bootstrap del proceso de citas
templates/citas/          pantallas del CRUD
templates/portal/         portal de propietarios y personal
static/                   estilos del sitio
docs/                     diagramas vigentes y referencias anteriores
db.sqlite3                datos de prueba para ejecutar y demostrar el sistema
manage.py                 comandos de Django
requirements.txt          dependencias de Python
```

## Cómo ejecutar el proyecto

En Windows, abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
git clone https://github.com/yonnbarlizaperalta-wq/Clinica-veterinaria.git
cd Clinica-veterinaria
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\generar_entregable.ps1
.\.venv\Scripts\python.exe manage.py runserver
```

Abre <http://127.0.0.1:8000/>. Para el CRUD, inicia sesión desde `/acceder/` y visita `/citas/`. El panel administrativo está en `/admin/`. El script ejecuta migraciones y prepara usuarios y registros de demostración; no crea citas. Para probar el calendario y el CRUD, agenda una cita desde el propietario o recepción.

## Usuarios de prueba

| Rol | Usuario | Contraseña |
| --- | --- | --- |
| Administrador | `admin` | `Huellitas2026!` |
| Recepcionista | `recepcionista@demo.local` | `Recepcion2026!` |
| Propietario | `propietario1@demo.local` | `Propietario2026!` |
| Veterinaria: Ana Torres | `ana.torres@demo.local` | `AnaVet2026!` |
| Veterinario: Juan Ruiz | `juan.ruiz@demo.local` | `JuanVet2026!` |
| Veterinaria: Sofía Mora | `sofia.mora@demo.local` | `SofiaVet2026!` |

La cuenta del propietario está vinculada a Laura Pérez y Luna. Cada cuenta veterinaria se vincula con su propia ficha para separar sus agendas. Las credenciales son solo para la demostración académica local.
