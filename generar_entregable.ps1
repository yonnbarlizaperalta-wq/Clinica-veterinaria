param([string]$AdminUser = 'admin', [string]$AdminPassword = 'Huellitas2026!')
$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'Fallaron las migraciones.' }
$env:DEMO_ADMIN_USER = $AdminUser
$env:DEMO_ADMIN_PASSWORD = $AdminPassword
& $python manage.py crear_datos_demo
if ($LASTEXITCODE -ne 0) { throw 'Falló la carga de datos demo.' }
& $python manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Falló Django system check.' }
Write-Host 'Sistema preparado. Inicia con: .\.venv\Scripts\python.exe manage.py runserver'
