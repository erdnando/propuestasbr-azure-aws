# Generador de Scripts para SQL Server

Aplicación en Python empaquetada para ejecutarse dentro de un contenedor Linux. Extrae metadatos de una base de datos SQL Server y genera:

- Un archivo `full_ddl.sql` con la definición completa de la base de datos: esquemas, tipos definidos por el usuario (escalares y de tabla), secuencias, tablas, constraints (DEFAULT/CHECK/UNIQUE/FOREIGN KEY), índices, vistas, funciones, stored procedures, triggers y sinónimos.
- Un archivo opcional `full_dml.sql` con los `INSERT` para las tablas seleccionadas, generado en lotes para soportar volúmenes grandes.

## Requisitos

- Docker
- Acceso a la instancia de SQL Server (puede ser local o remota).

## Configuración

1. Duplica el archivo `config/example_config.yml` y actualiza tus credenciales.

```yaml
  include_functions: []
  include_triggers: []
  include_sequences: []
  include_synonyms: []
  include_table_types: []
  include_user_types: []
database:
  server: localhost
  port: 1433
  database: AdventureWorks
  username: sa
  password: ${SQLSERVER_PASSWORD}
  include_default_constraints: true
  include_check_constraints: true
  include_foreign_keys: true
  include_unique_constraints: true
  include_indexes: true
  include_functions: true
  include_triggers: true
  include_sequences: true
  include_synonyms: true
  include_user_types: true
  include_table_types: true
  schema: dbo
  include_tables: []
  include_views: []
  include_procedures: []
> Deja las listas `include_*` vacías para incluir todo, o indícalas (con o sin esquema) para filtrar objetos específicos.
output:
  directory: output
  include_data: true
  rows_per_table: null
  batch_size: 5000
```

> Usa `null` (o elimina el campo) en `rows_per_table` para traer todas las filas.
> Ajusta `batch_size` para controlar cuántas filas procesa el contenedor por lote cuando genera los INSERT.
> Deja las listas `include_tables`, `include_views` e `include_procedures` vacías para incluir todo, o indícalas (con o sin esquema) para filtrar objetos específicos.
> Puedes usar variables de entorno con la sintaxis `${VARIABLE}` para evitar exponer contraseñas.

## Construcción de la imagen

```bash
docker build -t sqlscript-generator .
```

## Ejecución

```bash
docker run --rm \
  -e SQLSERVER_PASSWORD="TuPassword" \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/salida:/app/output \
  sqlscript-generator \
  generate -c config/example_config.yml
```

### Parámetros adicionales

- `--no-data`: genera solo DDL.
- `--rows-per-table <n>`: limita el número de filas por tabla en los INSERT (omite el flag para traer todo).
- `--batch-size <n>`: tamaño de lote para procesar filas (por defecto 5000).
- `--include-table <tabla>`: agrega una o varias tablas específicas.
- `--include-view <vista>`: filtra vistas específicas (puedes repetir la bandera).
- `--include-procedure <sp>`: filtra stored procedures específicas (puedes repetir la bandera).
- `--no-default-constraints`, `--no-check-constraints`, `--no-foreign-keys`, `--no-unique-constraints`: permiten omitir cada tipo de constraint.
- `--no-indexes`, `--no-functions`, `--no-triggers`, `--no-sequences`, `--no-synonyms`, `--no-user-types`, `--no-table-types`: deshabilitan secciones específicas del DDL agregado.

## Desarrollo local

1. Crear entorno virtual e instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Ejecutar pruebas:

```bash

El archivo `full_ddl.sql` se organiza en secciones con comentarios para facilitar su navegación (schemas, tipos, secuencias, tablas, constraints, índices, vistas, módulos, triggers y sinónimos). Cada bloque termina en `GO` cuando es necesario para preservar la semántica de SQL Server.
pytest
```

## Estructura de salida

```
output/
├── full_ddl.sql
└── full_dml.sql
```

## Licencia

MIT
