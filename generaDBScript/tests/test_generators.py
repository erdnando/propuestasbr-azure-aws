from __future__ import annotations

from decimal import Decimal

from app.generators.constraint_generator import ConstraintGenerator
from app.generators.ddl_generator import DDLGenerator
from app.generators.dml_generator import DMLGenerator
from app.generators.function_generator import FunctionGenerator
from app.generators.index_generator import IndexGenerator
from app.generators.procedure_generator import ProcedureGenerator
from app.generators.sequence_generator import SequenceGenerator
from app.generators.synonym_generator import SynonymGenerator
from app.generators.trigger_generator import TriggerGenerator
from app.generators.type_generator import TypeGenerator
from app.generators.view_generator import ViewGenerator
from app.models import (
    CheckConstraintMetadata,
    DefaultConstraintMetadata,
    FunctionMetadata,
    IndexColumnMetadata,
    IndexMetadata,
    ProcedureMetadata,
    SequenceMetadata,
    SynonymMetadata,
    TableColumn,
    TableMetadata,
    TableTypeColumnMetadata,
    TableTypeMetadata,
    TriggerMetadata,
    UniqueConstraintMetadata,
    ViewMetadata,
)


def build_sample_table() -> TableMetadata:
    columns = [
        TableColumn(
            name="Id",
            data_type="int",
            character_max_length=None,
            numeric_precision=10,
            numeric_scale=0,
            is_nullable=False,
            column_default=None,
            is_identity=True,
        ),
        TableColumn(
            name="Name",
            data_type="nvarchar",
            character_max_length=50,
            numeric_precision=None,
            numeric_scale=None,
            is_nullable=False,
            column_default=None,
        ),
        TableColumn(
            name="Balance",
            data_type="decimal",
            character_max_length=None,
            numeric_precision=18,
            numeric_scale=2,
            is_nullable=True,
            column_default=None,
        ),
    ]

    table = TableMetadata(schema="dbo", name="Customer", columns=columns, primary_keys=["Id"])
    table.data = [
        {"Id": 1, "Name": "Alice", "Balance": Decimal("10.50")},
        {"Id": 2, "Name": "O'Connor", "Balance": None},
    ]
    return table


def test_generate_ddl() -> None:
    table = build_sample_table()
    ddl = DDLGenerator().generate(table)

    assert "CREATE TABLE [dbo].[Customer]" in ddl
    assert "[Id] INT IDENTITY(1,1) NOT NULL" in ddl
    assert "CONSTRAINT [PK_dbo_Customer] PRIMARY KEY ([Id])" in ddl


def test_generate_dml() -> None:
    table = build_sample_table()
    dml = DMLGenerator().build_statement(table, table.data)
    assert dml is not None
    assert "INSERT INTO [dbo].[Customer] ([Id], [Name], [Balance]) VALUES" in dml
    assert "O''Connor" in dml
    assert "NULL" in dml


def test_write_batches(tmp_path) -> None:
    table = build_sample_table()
    generator = DMLGenerator()
    batch_one = table.data[:1]
    batch_two = table.data[1:]
    aggregate_path = tmp_path / "full_dml.sql"

    with aggregate_path.open("w", encoding="utf-8") as aggregate_file:
        wrote = generator.write_batches(table, [batch_one, batch_two], aggregate_file)

    assert wrote is True
    aggregate_content = aggregate_path.read_text(encoding="utf-8")
    assert aggregate_content.count("INSERT INTO [dbo].[Customer]") == 2
    assert "O''Connor" in aggregate_content


def test_view_generator_normalizes_create() -> None:
    generator = ViewGenerator()
    raw_definition = "SET ANSI_NULLS ON\nSET QUOTED_IDENTIFIER ON\nCREATE VIEW [dbo].[vwTest] AS SELECT 1 AS Col"
    view = ViewMetadata(schema="dbo", name="vwTest", definition=raw_definition)
    script = generator.generate(view)
    assert "CREATE OR ALTER VIEW" in script
    assert "GO" in script


def test_procedure_generator_handles_definition() -> None:
    generator = ProcedureGenerator()
    raw_definition = "CREATE PROCEDURE [dbo].[uspDoSomething] AS SELECT GETDATE();"
    procedure = ProcedureMetadata(schema="dbo", name="uspDoSomething", definition=raw_definition)
    script = generator.generate(procedure)
    assert "CREATE OR ALTER PROCEDURE" in script
    assert script.strip().endswith("GO")


def test_constraint_generator_default() -> None:
    generator = ConstraintGenerator()
    constraint = DefaultConstraintMetadata(
        schema="dbo",
        table_name="Customer",
        column_name="Status",
        name="DF_Customer_Status",
        definition="((1))",
        is_system_named=False,
    )
    statement = generator.default_constraint(constraint)
    assert "DEFAULT ((1))" in statement
    assert "FOR [Status]" in statement


def test_constraint_generator_check_states() -> None:
    generator = ConstraintGenerator()
    constraint = CheckConstraintMetadata(
        schema="dbo",
        table_name="Customer",
        name="CK_Customer_Balance",
        definition="([Balance] >= (0))",
        is_not_trusted=True,
        is_disabled=False,
    )
    statement = generator.check_constraint(constraint)
    assert "WITH NOCHECK ADD" in statement
    assert "WITH NOCHECK CHECK" in statement


def test_constraint_generator_unique() -> None:
    generator = ConstraintGenerator()
    constraint = UniqueConstraintMetadata(
        schema="dbo",
        table_name="Customer",
        name="UQ_Customer_Email",
        columns=["Email"],
        type_desc="NONCLUSTERED",
    )
    statement = generator.unique_constraint(constraint)
    assert "UNIQUE NONCLUSTERED" in statement


def test_index_generator_statement() -> None:
    generator = IndexGenerator()
    index = IndexMetadata(
        schema="dbo",
        table_name="Customer",
        name="IX_Customer_Name",
        type_desc="NONCLUSTERED",
        is_unique=False,
        is_disabled=False,
        filter_definition=None,
        columns=[
            IndexColumnMetadata(name="Name", is_descending=False, is_included=False, ordinal=1),
            IndexColumnMetadata(name="IsActive", is_descending=False, is_included=True, ordinal=1001),
        ],
    )
    statement = generator.generate(index)
    assert "CREATE NONCLUSTERED INDEX" in statement
    assert "INCLUDE ([IsActive])" in statement


def test_function_generator_normalizes_create() -> None:
    generator = FunctionGenerator()
    fn = FunctionMetadata(
        schema="dbo",
        name="fnAddOne",
        type="FN",
        definition="CREATE FUNCTION [dbo].[fnAddOne](@value INT) RETURNS INT AS BEGIN RETURN @value + 1 END",
    )
    script = generator.generate(fn)
    assert "CREATE OR ALTER FUNCTION" in script


def test_trigger_generator_normalizes_create() -> None:
    generator = TriggerGenerator()
    trigger = TriggerMetadata(
        schema="dbo",
        table_schema="dbo",
        table_name="Customer",
        name="tr_Customer_Audit",
        definition="CREATE TRIGGER [dbo].[tr_Customer_Audit] ON [dbo].[Customer] AFTER INSERT AS BEGIN SET NOCOUNT ON; END",
        is_instead_of=False,
    )
    script = generator.generate(trigger)
    assert "CREATE OR ALTER TRIGGER" in script


def test_sequence_generator_outputs_clause() -> None:
    generator = SequenceGenerator()
    sequence = SequenceMetadata(
        schema="dbo",
        name="seqCustomer",
        data_type="INT",
        start_value=1,
        increment=1,
        minimum_value=1,
        maximum_value=None,
        is_cycling=False,
        cache_size=50,
    )
    script = generator.generate(sequence)
    assert "CREATE SEQUENCE" in script
    assert "CACHE 50" in script


def test_synonym_generator_output() -> None:
    generator = SynonymGenerator()
    script = generator.generate(
        SynonymMetadata(schema="dbo", name="SynCustomer", base_object_name="OtherDb.dbo.Customer")
    )
    assert "DROP SYNONYM" in script
    assert "CREATE SYNONYM" in script


def test_type_generator_table_type() -> None:
    generator = TypeGenerator()
    table_type = TableTypeMetadata(
        schema="dbo",
        name="CustomerTableType",
        columns=[
            TableTypeColumnMetadata(
                name="Id",
                data_type="int",
                character_max_length=None,
                numeric_precision=10,
                numeric_scale=0,
                is_nullable=False,
                is_identity=True,
                column_default=None,
            ),
            TableTypeColumnMetadata(
                name="Name",
                data_type="nvarchar",
                character_max_length=50,
                numeric_precision=None,
                numeric_scale=None,
                is_nullable=True,
                is_identity=False,
                column_default=None,
            ),
        ],
        primary_keys=["Id"],
    )
    script = generator.generate_table_type(table_type)
    assert "CREATE TYPE [dbo].[CustomerTableType] AS TABLE" in script
    assert "PRIMARY KEY" in script
