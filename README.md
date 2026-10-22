# Clínica veterinaria Huellitas

Sistema web académico para gestionar una clínica veterinaria. Permite registrar propietarios y mascotas, solicitar y administrar citas, consultar historias clínicas y llevar el registro de las vacunas aplicadas. Los cambios se guardan en una base de datos SQLite local.

## Equipo

- Yonn Barliza
- Luis José López
- Yair Ospino

## Funcionalidades

- **Propietarios:** crean una cuenta, registran sus mascotas, solicitan citas y consultan el calendario, las historias clínicas y las vacunas de sus propias mascotas. La cuenta de demostración también permite recorrer este flujo.
- **Recepcionista:** consulta la agenda de la clínica y agenda citas para los propietarios y sus mascotas.
- **Veterinario:** consulta y atiende las citas asignadas a su ficha, actualiza la historia clínica y registra vacunas.
- **Administrador:** gestiona los usuarios, los grupos de permisos y los datos de la clínica desde Django Admin. Vincula la cuenta de cada veterinario con su ficha.
- **Calendario:** muestra las citas guardadas en la base de datos. Si no hay citas registradas para el usuario o mes seleccionado, no muestra citas.

## Requisitos

- Python 3.10 o superior.
- Windows PowerShell para usar el script de instalación incluido.

## Instalación y ejecución en Windows

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\generar_entregable.ps1
.\.venv\Scripts\python.exe manage.py runserver
```

Abre el sitio en <http://127.0.0.1:8000/>. El script prepara las migraciones, datos de demostración y la cuenta administradora. No genera citas de demostración; estas se crean al solicitarlas desde el portal o agendarlas desde recepción.

Para preparar la base de datos sin el script, ejecuta:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py crear_datos_demo
.\.venv\Scripts\python.exe manage.py runserver
```

## Acceso al sistema

- **Sitio público y portal:** <http://127.0.0.1:8000/>
- **Propietarios y personal:** selecciona “Acceso clientes y equipo” o visita <http://127.0.0.1:8000/acceder/>. El sistema dirige a cada persona al panel según su cuenta.
- **Administración:** <http://127.0.0.1:8000/admin/>. Cuenta de demostración inicial: `admin` / `Huellitas2026!`.

Cuentas demostrativas para probar el sistema:

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin` | `Huellitas2026!` |
| Recepcionista | `recepcionista@demo.local` | `Recepcion2026!` |
| Propietario | `propietario1@demo.local` | `Propietario2026!` |
| Veterinaria: Ana Torres | `ana.torres@demo.local` | `AnaVet2026!` |
| Veterinario: Juan Ruiz | `juan.ruiz@demo.local` | `JuanVet2026!` |
| Veterinaria: Sofía Mora | `sofia.mora@demo.local` | `SofiaVet2026!` |

La cuenta de propietario está vinculada a Laura Pérez y a su mascota Luna. Cada cuenta veterinaria está vinculada a su propia ficha; la agenda y las consultas de cada veterinario muestran solo las citas asignadas a esa ficha. Así se pueden probar las citas de Juan y Sofía por separado. El calendario no contiene citas ficticias: las citas de prueba se crean desde el portal del propietario o desde recepción. Estas credenciales son solo para la demostración local; cámbialas antes de cualquier despliegue.

Para crear cuentas reales del equipo, el administrador crea el usuario en Django Admin, lo agrega al grupo `Recepcionista` o `Veterinario` y, si es veterinario, lo vincula también en la ficha correspondiente desde **Veterinarios**.

## Modelo de datos

El sistema organiza la información en siete entidades principales: Propietario, Mascota, Historia clínica, Veterinario, Cita, Vacuna y Aplicación de vacuna. Cada propietario puede tener varias mascotas; cada mascota tiene su historia clínica; y la aplicación de vacuna registra la relación entre mascota y vacuna junto con la fecha, dosis, lote y próxima fecha. Cada cita queda vinculada a una mascota y a un veterinario.

Diagramas: [casos de uso](docs/diagrama_actores.pdf) y [entidad-relación](docs/diagrama_er.pdf).

## Aplicaciones Django

| Aplicación | Entidad |
|---|---|
| `propietarios_core` | Propietario |
| `mascotas` | Mascota |
| `historias_clinicas` | Historia clínica |
| `veterinarios` | Veterinario y su cuenta asignada |
| `citas` | Cita |
| `vacunas` | Vacuna |
| `aplicaciones_vacuna` | Aplicación de vacuna |

## Base de datos

SQLite se configura automáticamente en `db.sqlite3`. Ese archivo se crea localmente y está excluido de Git para que no se publiquen datos de propietarios. Las migraciones se encuentran en cada aplicación Django. Para inicializar una instalación nueva, ejecuta `generar_entregable.ps1`.

## Solución de problemas en VS Code

Si Pylance muestra `Import "django" could not be resolved`, selecciona el intérprete `.venv\Scripts\python.exe` mediante **Ctrl+Shift+P → Python: Select Interpreter**. Si el entorno aún no está instalado, ejecuta los pasos de instalación anteriores.
