from __future__ import annotations

from typing import Optional

from app.models import TableTypeMetadata, TableTypeColumnMetadata, UserDefinedTypeMetadata


class TypeGenerator:
    def generate_user_defined_type(self, user_type: UserDefinedTypeMetadata) -> str:
        data_type = self._render_data_type(
            user_type.underlying_system_type,
            user_type.max_length,
            user_type.precision,
            user_type.scale,
        )
        statement = f"CREATE TYPE {user_type.full_name} FROM {data_type}"
        if not user_type.is_nullable:
            statement += " NOT NULL"
        statement += ";\nGO"
        return statement

    def generate_table_type(self, table_type: TableTypeMetadata) -> str:
        column_lines = [
            self._render_table_type_column(column) for column in table_type.columns
        ]
        if table_type.primary_keys:
            pk_columns = ", ".join(f"[{col}]" for col in table_type.primary_keys)
            column_lines.append(
                f"    CONSTRAINT [PK_{table_type.schema}_{table_type.name}] PRIMARY KEY ({pk_columns})"
            )
        body = ",\n".join(column_lines)
        return f"CREATE TYPE {table_type.full_name} AS TABLE (\n{body}\n);\nGO"

    def _render_table_type_column(self, column: TableTypeColumnMetadata) -> str:
        data_type = self._render_data_type(
            column.data_type,
            column.character_max_length,
            column.numeric_precision,
            column.numeric_scale,
        )
        parts = [f"    [{column.name}]", data_type]
        if column.is_identity:
            parts.append("IDENTITY(1,1)")
        parts.append("NOT NULL" if not column.is_nullable else "NULL")
        if column.column_default:
            parts.append(f"DEFAULT {column.column_default.strip()}")
        return " ".join(parts)

    def _render_data_type(
        self,
        data_type: str,
        max_length: Optional[int],
        precision: Optional[int],
        scale: Optional[int],
    ) -> str:
        upper = data_type.upper()
        if upper in {"NVARCHAR", "NCHAR"}:
            length = "MAX" if max_length in (-1, None) else str(max_length // 2)
            return f"{upper}({length})"
        if upper in {"VARCHAR", "CHAR", "VARBINARY", "BINARY"}:
            length = "MAX" if max_length in (-1, None) else str(max_length)
            return f"{upper}({length})"
        if upper in {"DECIMAL", "NUMERIC"}:
            prec = precision or 18
            sc = scale or 0
            return f"{upper}({prec},{sc})"
        if upper in {"DATETIME2", "TIME", "DATETIMEOFFSET"} and scale is not None:
            return f"{upper}({scale})"
        return upper
