from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, Iterable, Optional, Sequence, TextIO

from app.models import TableColumn, TableMetadata


class DMLGenerator:
    def build_statement(self, table: TableMetadata, rows: Sequence[Dict[str, Any]]) -> Optional[str]:
        if not rows:
            return None

        column_names = [column.name for column in table.columns]
        header = ", ".join(f"[{name}]" for name in column_names)
        value_lines = []
        for row in rows:
            values = [self._format_value(row.get(name), table.columns[idx]) for idx, name in enumerate(column_names)]
            value_lines.append(f"    ({', '.join(values)})")

        statement = ",\n".join(value_lines)
        return f"INSERT INTO {table.full_name} ({header}) VALUES\n{statement};"

    def write_batches(
        self,
        table: TableMetadata,
        row_batches: Iterable[Sequence[Dict[str, Any]]],
        aggregate_file: TextIO,
    ) -> bool:
        wrote_rows = False

        for batch in row_batches:
            statement = self.build_statement(table, batch)
            if not statement:
                continue
            aggregate_file.write(statement + "\n\n")
            wrote_rows = True

        return wrote_rows

    def _format_value(self, value, column: TableColumn) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, str):
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        if isinstance(value, (datetime, date, time)):
            return f"'{value.isoformat()}'"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, Decimal):
            return format(value, 'f').rstrip('0').rstrip('.') if '.' in format(value, 'f') else format(value, 'f')
        return str(value)
