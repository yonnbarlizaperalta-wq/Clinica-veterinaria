# Diagramas del sistema

Los PNG y los archivos editables `.drawio` se actualizaron juntos y presentan los mismos nombres, relaciones y casos de uso. Se usa blanco y negro para que los elementos se distingan con claridad.

- `diagrama_actores.drawio`: diagrama editable de los actores y sus casos de uso.
- `diagrama_actores.pdf`: versión lista para entregar o imprimir. El PNG es una vista previa.
- `diagrama_er.drawio`: diagrama editable del modelo lógico, con tablas, campos, llaves y cardinalidades.
- `diagrama_er.pdf`: versión lista para entregar o imprimir. El PNG es una vista previa.

En el diagrama de datos, `PK` identifica la llave primaria, `FK` una llave foránea y `UNIQUE` un valor único. Las columnas de llaves conservan el prefijo `pk_` o `fk_` en minúscula, como en el código. `auth_user` es la tabla de cuentas de Django. La relación entre Mascota y Vacuna es muchos a muchos y se representa mediante `tbl_aplicacion_vacuna`, que guarda la fecha y la dosis. Las relaciones se acomodaron alrededor de las tablas para que sus líneas no se crucen.

Para editar un archivo, abre diagrams.net y selecciona **Archivo > Abrir desde > Dispositivo**.
