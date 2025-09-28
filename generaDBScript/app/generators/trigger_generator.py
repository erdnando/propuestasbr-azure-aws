from __future__ import annotations

import re

from app.models import TriggerMetadata


class TriggerGenerator:
    def generate(self, trigger: TriggerMetadata) -> str:
        definition = trigger.definition.strip()
        if not definition:
            return f"-- Trigger {trigger.full_name} sin definición disponible"
        normalized = self._ensure_create_or_alter(definition, trigger)
        return normalized.rstrip() + "\nGO"

    def _ensure_create_or_alter(self, definition: str, trigger: TriggerMetadata) -> str:
        pattern = re.compile(r"CREATE\s+(?:OR\s+ALTER\s+)?TRIGGER", re.IGNORECASE)
        match = pattern.search(definition)
        if match:
            return pattern.sub("CREATE OR ALTER TRIGGER", definition, count=1)
        return (
            f"CREATE OR ALTER TRIGGER {trigger.full_name}\n"
            f"ON {trigger.parent_full_name}\n"
            f"{definition}"
        )
