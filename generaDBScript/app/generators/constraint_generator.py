from __future__ import annotations

from app.models import (
    CheckConstraintMetadata,
    DefaultConstraintMetadata,
    ForeignKeyMetadata,
    UniqueConstraintMetadata,
)


class ConstraintGenerator:
    """Generates DDL statements for table-level constraints."""

    def default_constraint(self, constraint: DefaultConstraintMetadata) -> str:
        definition = constraint.definition.strip()
        return (
            f"ALTER TABLE {constraint.table_full_name} "
            f"ADD CONSTRAINT [{constraint.name}] DEFAULT {definition} FOR [{constraint.column_name}];"
        )

    def check_constraint(self, constraint: CheckConstraintMetadata) -> str:
        definition = constraint.definition.strip()
        with_clause = "WITH NOCHECK " if constraint.is_not_trusted or constraint.is_disabled else ""
        statements = [
            f"ALTER TABLE {constraint.table_full_name} {with_clause}ADD CONSTRAINT [{constraint.name}] CHECK {definition};"
        ]

        if constraint.is_disabled:
            statements.append(
                f"ALTER TABLE {constraint.table_full_name} NOCHECK CONSTRAINT [{constraint.name}];"
            )
        else:
            check_prefix = "WITH NOCHECK CHECK" if constraint.is_not_trusted else "WITH CHECK CHECK"
            statements.append(
                f"ALTER TABLE {constraint.table_full_name} {check_prefix} CONSTRAINT [{constraint.name}];"
            )
        return "\n".join(statements)

    def foreign_key(self, constraint: ForeignKeyMetadata) -> str:
        columns = ", ".join(f"[{col}]" for col in constraint.columns)
        referenced_columns = ", ".join(f"[{col}]" for col in constraint.referenced_columns)
        with_clause = "WITH NOCHECK " if constraint.is_not_trusted or constraint.is_disabled else ""

        parts = [
            f"ALTER TABLE {constraint.table_full_name} {with_clause}ADD CONSTRAINT [{constraint.name}]",
            f"FOREIGN KEY ({columns}) REFERENCES {constraint.referenced_full_name} ({referenced_columns})",
        ]

        if constraint.delete_action and constraint.delete_action.upper() != "NO_ACTION":
            parts.append(f"ON DELETE {constraint.delete_action.replace('_', ' ')}")
        if constraint.update_action and constraint.update_action.upper() != "NO_ACTION":
            parts.append(f"ON UPDATE {constraint.update_action.replace('_', ' ')}")
        if constraint.is_not_for_replication:
            parts.append("NOT FOR REPLICATION")

        statements = [" ".join(parts) + ";"]
        if constraint.is_disabled:
            statements.append(
                f"ALTER TABLE {constraint.table_full_name} NOCHECK CONSTRAINT [{constraint.name}];"
            )
        else:
            check_prefix = "WITH NOCHECK CHECK" if constraint.is_not_trusted else "WITH CHECK CHECK"
            statements.append(
                f"ALTER TABLE {constraint.table_full_name} {check_prefix} CONSTRAINT [{constraint.name}];"
            )
        return "\n".join(statements)

    def unique_constraint(self, constraint: UniqueConstraintMetadata) -> str:
        index_type = self._map_index_type(constraint.type_desc)
        columns = ", ".join(f"[{col}]" for col in constraint.columns)
        clause = f"ALTER TABLE {constraint.table_full_name} ADD CONSTRAINT [{constraint.name}] UNIQUE"
        if index_type:
            clause += f" {index_type}"
        clause += f" ({columns});"
        return clause

    @staticmethod
    def _map_index_type(type_desc: str) -> str:
        if not type_desc:
            return ""
        upper = type_desc.upper()
        if "CLUSTERED" in upper and "NON" not in upper:
            return "CLUSTERED"
        if "NONCLUSTERED" in upper:
            return "NONCLUSTERED"
        return ""
