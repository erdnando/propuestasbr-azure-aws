from __future__ import annotations

from typing import List

from app.models import TableColumn, TableMetadata


class DDLGenerator:
    def generate(self, table: TableMetadata) -> str:
        column_lines = [self._build_column_definition(column) for column in table.columns]

        if table.primary_keys:
            pk_columns = ", ".join(f"[{col}]" for col in table.primary_keys)
            column_lines.append(
                f"    CONSTRAINT [PK_{table.schema}_{table.name}] PRIMARY KEY ({pk_columns})"
            )

        columns_block = ",\n".join(column_lines)
        return f"CREATE TABLE {table.full_name} (\n{columns_block}\n);"

    def _build_column_definition(self, column: TableColumn) -> str:
        pieces: List[str] = [f"    [{column.name}]", column.sql_type()]

        if column.is_identity:
            pieces.append("IDENTITY(1,1)")

        if not column.is_nullable:
            pieces.append("NOT NULL")
        else:
            pieces.append("NULL")

        return " ".join(pieces)
