from __future__ import annotations

from typing import List

from app.models import IndexMetadata


class IndexGenerator:
    """Generates CREATE INDEX statements for non constraint indexes."""

    def generate(self, index: IndexMetadata) -> str:
        parts: List[str] = ["CREATE"]
        if index.is_unique:
            parts.append("UNIQUE")

        index_type = self._map_index_type(index.type_desc)
        if index_type:
            parts.append(index_type)

        parts.append("INDEX")
        parts.append(f"[{index.name}]")
        parts.append("ON")
        parts.append(index.table_full_name)

        key_columns = ", ".join(self._format_column(col.name, col.is_descending) for col in index.key_columns)
        statement = " ".join(parts) + f" ({key_columns})"

        include_columns = index.include_columns
        if include_columns:
            include_clause = ", ".join(f"[{col.name}]" for col in include_columns)
            statement += f" INCLUDE ({include_clause})"

        if index.filter_definition:
            statement += f" WHERE {index.filter_definition.strip()}"

        statement += ";"

        if index.is_disabled:
            statement += f"\nALTER INDEX [{index.name}] ON {index.table_full_name} DISABLE;"

        return statement

    @staticmethod
    def _format_column(name: str, is_descending: bool) -> str:
        suffix = " DESC" if is_descending else " ASC"
        return f"[{name}]{suffix}"

    @staticmethod
    def _map_index_type(type_desc: str) -> str:
        if not type_desc:
            return ""
        upper = type_desc.upper()
        if "COLUMNSTORE" in upper:
            prefix = "CLUSTERED" if "CLUSTERED" in upper else "NONCLUSTERED"
            return f"{prefix} COLUMNSTORE"
        if "HASH" in upper:
            return upper.replace("_", " ")
        if "CLUSTERED" in upper and "NON" not in upper:
            return "CLUSTERED"
        if "NONCLUSTERED" in upper:
            return "NONCLUSTERED"
        return ""
