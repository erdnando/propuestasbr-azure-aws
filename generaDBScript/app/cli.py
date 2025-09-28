from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional
import shutil

import click

from app.config import build_config
from app.generators.ddl_generator import DDLGenerator
from app.generators.dml_generator import DMLGenerator
from app.generators.constraint_generator import ConstraintGenerator
from app.generators.function_generator import FunctionGenerator
from app.generators.index_generator import IndexGenerator
from app.generators.procedure_generator import ProcedureGenerator
from app.generators.sequence_generator import SequenceGenerator
from app.generators.synonym_generator import SynonymGenerator
from app.generators.trigger_generator import TriggerGenerator
from app.generators.type_generator import TypeGenerator
from app.generators.view_generator import ViewGenerator
from app.services.metadata_extractor import MetadataExtractor


@click.group()
def cli() -> None:
    """CLI principal para generar scripts de SQL Server."""


def _clear_directory(path: Path) -> None:
    if not path.exists():
        return
    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


@cli.command("generate")
@click.option("config_path", "-c", "--config", type=click.Path(exists=True, path_type=Path), required=True, help="Ruta al archivo YAML de configuración.")
@click.option("--server", type=str, help="Servidor de SQL Server")
@click.option("--database", type=str, help="Nombre de la base de datos")
@click.option("--username", type=str, help="Usuario de SQL Server")
@click.option("--password", type=str, help="Contraseña de SQL Server")
@click.option("--port", type=int, help="Puerto del servidor")
@click.option("--schema", type=str, help="Schema a inspeccionar")
@click.option("--include-table", multiple=True, help="Tabla(s) específicas a incluir")
@click.option("--include-view", multiple=True, help="Vista(s) específicas a incluir")
@click.option("--include-procedure", multiple=True, help="Stored procedure(s) específicas a incluir")
@click.option("--output-dir", type=click.Path(path_type=Path), help="Directorio de salida para los scripts")
@click.option("--no-data", is_flag=True, default=False, help="No generar INSERTs, solo DDL")
@click.option("--rows-per-table", type=int, help="Número máximo de filas por tabla para INSERTs")
@click.option("--batch-size", type=int, help="Número de filas a leer por lote (por defecto 5000)")
@click.option("--no-default-constraints", is_flag=True, default=False, help="Omitir la generación de constraints DEFAULT")
@click.option("--no-check-constraints", is_flag=True, default=False, help="Omitir la generación de constraints CHECK")
@click.option("--no-foreign-keys", is_flag=True, default=False, help="Omitir la generación de llaves foráneas")
@click.option("--no-unique-constraints", is_flag=True, default=False, help="Omitir constraints UNIQUE")
@click.option("--no-indexes", is_flag=True, default=False, help="Omitir índices que no formen parte de constraints")
@click.option("--no-functions", is_flag=True, default=False, help="Omitir funciones definidas por el usuario")
@click.option("--no-triggers", is_flag=True, default=False, help="Omitir triggers")
@click.option("--no-sequences", is_flag=True, default=False, help="Omitir secuencias")
@click.option("--no-synonyms", is_flag=True, default=False, help="Omitir sinónimos")
@click.option("--no-user-types", is_flag=True, default=False, help="Omitir tipos definidos por el usuario")
@click.option("--no-table-types", is_flag=True, default=False, help="Omitir tipos de tabla")
def generate_command(
    config_path: Path,
    server: Optional[str],
    database: Optional[str],
    username: Optional[str],
    password: Optional[str],
    port: Optional[int],
    schema: Optional[str],
    include_table: Optional[list[str]],
    include_view: Optional[list[str]],
    include_procedure: Optional[list[str]],
    output_dir: Optional[Path],
    no_data: bool,
    rows_per_table: Optional[int],
    batch_size: Optional[int],
    no_default_constraints: bool,
    no_check_constraints: bool,
    no_foreign_keys: bool,
    no_unique_constraints: bool,
    no_indexes: bool,
    no_functions: bool,
    no_triggers: bool,
    no_sequences: bool,
    no_synonyms: bool,
    no_user_types: bool,
    no_table_types: bool,
) -> None:
    overrides: Dict[str, Dict[str, object]] = {"database": {}, "output": {}}

    if server:
        overrides["database"]["server"] = server
    if database:
        overrides["database"]["database"] = database
    if username:
        overrides["database"]["username"] = username
    if password:
        overrides["database"]["password"] = password
    if port:
        overrides["database"]["port"] = port
    if schema:
        overrides["database"]["schema"] = schema
    if include_table:
        overrides["database"]["include_tables"] = list(include_table)
    if include_view:
        overrides["database"]["include_views"] = list(include_view)
    if include_procedure:
        overrides["database"]["include_procedures"] = list(include_procedure)
    if output_dir:
        overrides["output"]["directory"] = output_dir
    if rows_per_table is not None:
        overrides["output"]["rows_per_table"] = rows_per_table
    if batch_size is not None:
        overrides["output"]["batch_size"] = batch_size
    if no_data:
        overrides["output"]["include_data"] = False
    if no_default_constraints:
        overrides["output"]["include_default_constraints"] = False
    if no_check_constraints:
        overrides["output"]["include_check_constraints"] = False
    if no_foreign_keys:
        overrides["output"]["include_foreign_keys"] = False
    if no_unique_constraints:
        overrides["output"]["include_unique_constraints"] = False
    if no_indexes:
        overrides["output"]["include_indexes"] = False
    if no_functions:
        overrides["output"]["include_functions"] = False
    if no_triggers:
        overrides["output"]["include_triggers"] = False
    if no_sequences:
        overrides["output"]["include_sequences"] = False
    if no_synonyms:
        overrides["output"]["include_synonyms"] = False
    if no_user_types:
        overrides["output"]["include_user_types"] = False
    if no_table_types:
        overrides["output"]["include_table_types"] = False

    config = build_config(config_path, overrides)
    output_directory = config.ensure_output_dir()
    _clear_directory(output_directory)

    click.echo(f"Extrayendo metadatos desde {config.database.server}/{config.database.database}...")

    extractor = MetadataExtractor(config.database)
    metadata = extractor.extract()

    if not metadata.tables and not metadata.views and not metadata.procedures:
        click.echo("No se encontraron objetos con los filtros proporcionados.")
        return

    ddl_generator = DDLGenerator()
    dml_generator = DMLGenerator()
    view_generator = ViewGenerator()
    procedure_generator = ProcedureGenerator()
    function_generator = FunctionGenerator()
    trigger_generator = TriggerGenerator()
    constraint_generator = ConstraintGenerator()
    index_generator = IndexGenerator()
    sequence_generator = SequenceGenerator()
    synonym_generator = SynonymGenerator()
    type_generator = TypeGenerator()

    full_ddl_path = output_directory / "full_ddl.sql"
    full_dml_path = output_directory / "full_dml.sql"

    with full_ddl_path.open("w", encoding="utf-8") as full_ddl_file:
        def write_section(title: str, statements: list[str]) -> None:
            if not statements:
                return
            full_ddl_file.write(f"-- {title}\n")
            for statement in statements:
                full_ddl_file.write(statement.strip() + "\n\n")

        schema_statements = [
            (
                "IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = '{0}')\n"
                "    EXEC('CREATE SCHEMA [{0}]');\nGO".format(schema)
            )
            for schema in metadata.schemas
            if schema.lower() != "dbo"
        ]
        write_section("SCHEMAS", schema_statements)

        if config.output.include_user_types:
            user_type_statements = [
                type_generator.generate_user_defined_type(user_type)
                for user_type in metadata.user_defined_types
            ]
            write_section("USER DEFINED TYPES", user_type_statements)

        if config.output.include_table_types:
            table_type_statements = [
                type_generator.generate_table_type(table_type)
                for table_type in metadata.table_types
            ]
            write_section("TABLE TYPES", table_type_statements)

        if config.output.include_sequences:
            sequence_statements = [sequence_generator.generate(seq) for seq in metadata.sequences]
            write_section("SEQUENCES", sequence_statements)

        table_statements = [ddl_generator.generate(table) for table in metadata.tables]
        write_section("TABLES", table_statements)

        if config.output.include_default_constraints:
            default_statements = [
                constraint_generator.default_constraint(constraint)
                for constraint in metadata.default_constraints
            ]
            write_section("DEFAULT CONSTRAINTS", default_statements)

        if config.output.include_check_constraints:
            check_statements = [
                constraint_generator.check_constraint(constraint)
                for constraint in metadata.check_constraints
            ]
            write_section("CHECK CONSTRAINTS", check_statements)

        if config.output.include_unique_constraints:
            unique_statements = [
                constraint_generator.unique_constraint(constraint)
                for constraint in metadata.unique_constraints
            ]
            write_section("UNIQUE CONSTRAINTS", unique_statements)

        if config.output.include_foreign_keys:
            foreign_key_statements = [
                constraint_generator.foreign_key(constraint)
                for constraint in metadata.foreign_keys
            ]
            write_section("FOREIGN KEYS", foreign_key_statements)

        if config.output.include_indexes:
            index_statements = [index_generator.generate(index) for index in metadata.indexes]
            write_section("INDEXES", index_statements)

        if metadata.views:
            view_statements = [view_generator.generate(view) for view in metadata.views]
            write_section("VIEWS", view_statements)

        if config.output.include_functions:
            function_statements = [function_generator.generate(fn) for fn in metadata.functions]
            write_section("FUNCTIONS", function_statements)

        procedure_statements = [
            procedure_generator.generate(procedure) for procedure in metadata.procedures
        ]
        write_section("STORED PROCEDURES", procedure_statements)

        if config.output.include_triggers:
            trigger_statements = [trigger_generator.generate(trigger) for trigger in metadata.triggers]
            write_section("TRIGGERS", trigger_statements)

        if config.output.include_synonyms:
            synonym_statements = [synonym_generator.generate(synonym) for synonym in metadata.synonyms]
            write_section("SYNONYMS", synonym_statements)

    if config.output.include_data:
        wrote_any = False
        with full_dml_path.open("w", encoding="utf-8") as full_dml_file:
            for table in metadata.tables:
                row_batches = extractor.stream_table_rows(
                    table,
                    rows_per_table=config.output.rows_per_table,
                    batch_size=config.output.batch_size,
                )
                if dml_generator.write_batches(table, row_batches, full_dml_file):
                    wrote_any = True
        if not wrote_any:
            full_dml_path.unlink(missing_ok=True)

    click.echo(f"Scripts generados en {output_directory.resolve()}")
