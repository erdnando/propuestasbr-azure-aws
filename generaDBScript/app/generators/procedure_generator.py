from __future__ import annotations

import re

from app.models import ProcedureMetadata


class ProcedureGenerator:
    def generate(self, procedure: ProcedureMetadata) -> str:
        definition = procedure.definition.strip()
        if not definition:
            return f"-- Stored procedure {procedure.full_name} sin definición disponible"
        normalized = self._ensure_create_or_alter(definition, procedure.full_name)
        return normalized.rstrip() + "\nGO"

    def _ensure_create_or_alter(self, definition: str, full_name: str) -> str:
        pattern = re.compile(r"CREATE\s+(?:OR\s+ALTER\s+)?PROCEDURE", re.IGNORECASE)
        match = pattern.search(definition)
        if match:
            return pattern.sub("CREATE OR ALTER PROCEDURE", definition, count=1)
        return f"CREATE OR ALTER PROCEDURE {full_name}\nAS\n{definition}"
