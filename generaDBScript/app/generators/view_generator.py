from __future__ import annotations

import re

from app.models import ViewMetadata


class ViewGenerator:
    def generate(self, view: ViewMetadata) -> str:
        definition = view.definition.strip()
        if not definition:
            return f"-- View {view.full_name} sin definición disponible"
        normalized = self._ensure_create_or_alter(definition, view.full_name)
        return normalized.rstrip() + "\nGO"

    def _ensure_create_or_alter(self, definition: str, full_name: str) -> str:
        pattern = re.compile(r"CREATE\s+(?:OR\s+ALTER\s+)?VIEW", re.IGNORECASE)
        match = pattern.search(definition)
        if match:
            return pattern.sub("CREATE OR ALTER VIEW", definition, count=1)
        return f"CREATE OR ALTER VIEW {full_name}\nAS\n{definition}"
