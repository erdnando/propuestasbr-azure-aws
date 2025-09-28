from __future__ import annotations

from app.models import SynonymMetadata


class SynonymGenerator:
    def generate(self, synonym: SynonymMetadata) -> str:
        return (
            f"IF OBJECT_ID('{synonym.full_name}', 'SN') IS NOT NULL\n"
            f"    DROP SYNONYM {synonym.full_name};\n"
            f"CREATE SYNONYM {synonym.full_name} FOR {synonym.base_object_name};\nGO"
        )
