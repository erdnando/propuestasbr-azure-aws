from __future__ import annotations

import re

from app.models import FunctionMetadata


class FunctionGenerator:
    def generate(self, function: FunctionMetadata) -> str:
        definition = function.definition.strip()
        if not definition:
            return f"-- Función {function.full_name} sin definición disponible"
        normalized = self._ensure_create_or_alter(definition, function.full_name)
        return normalized.rstrip() + "\nGO"

    def _ensure_create_or_alter(self, definition: str, full_name: str) -> str:
        pattern = re.compile(r"CREATE\s+(?:OR\s+ALTER\s+)?FUNCTION", re.IGNORECASE)
        match = pattern.search(definition)
        if match:
            return pattern.sub("CREATE OR ALTER FUNCTION", definition, count=1)
        return f"-- Definición original de {full_name} sin encabezado CREATE FUNCTION normalizable\n{definition}"
