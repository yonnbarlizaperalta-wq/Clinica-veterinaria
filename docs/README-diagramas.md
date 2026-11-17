# Diagramas del sistema

Los PNG y los archivos editables `.drawio` se actualizaron juntos y presentan los mismos nombres, relaciones y casos de uso. Se usa blanco y negro para que los elementos se distingan con claridad.

- `diagrama_actores.drawio` y `diagrama_actores.png`: funciones del Administrador, Recepcionista, Veterinario y Propietario. Incluye solicitar, reprogramar y cancelar citas.
- `diagrama_er.drawio` y `diagrama_er.png`: modelo lógico con las tablas, campos, llaves y cardinalidades que corresponden a los modelos Django.
- Los PDF con el mismo nombre son versiones vectoriales de los diagramas.
- Los diagramas del segundo corte se conservan en los PDF que terminan en `_segundo_corte`.

En el diagrama de datos, `PK` identifica la llave primaria, `FK` una llave foránea y `UNIQUE` un valor único. Las columnas de llaves conservan el prefijo `pk_` o `fk_` en minúscula, como en el código. `auth_user` es la tabla de cuentas de Django. La relación entre Mascota y Vacuna es muchos a muchos y se representa mediante `tbl_aplicacion_vacuna`, que guarda la fecha y la dosis.

Para editar un archivo, abre diagrams.net y selecciona **Archivo > Abrir desde > Dispositivo**.
