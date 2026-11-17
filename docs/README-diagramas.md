# Diagramas del tercer corte

- `diagrama_actores.png`: límite del sistema, cuatro actores y al menos tres funciones conectadas para cada actor.
- `diagrama_er.png`: tablas y columnas de los modelos de la aplicación, con relaciones, llaves y cardinalidades. Se incluye `auth_user` de Django para mostrar los vínculos opcionales de propietario y veterinario.

Los nombres de tabla usan `tbl_`, las llaves primarias `pk_` y las llaves foráneas `fk_`. Los modelos Django declaran estos nombres en `db_table` y `db_column`; las migraciones correspondientes están dentro de cada app.

Los PDF con sufijo `_segundo_corte` se conservan como referencia histórica. Los PNG son los diagramas vigentes para la entrega.
