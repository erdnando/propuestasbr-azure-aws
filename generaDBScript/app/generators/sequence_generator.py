from __future__ import annotations

from app.models import SequenceMetadata


class SequenceGenerator:
    def generate(self, sequence: SequenceMetadata) -> str:
        parts = [
            f"CREATE SEQUENCE {sequence.full_name}",
            f"AS {sequence.data_type}",
            f"START WITH {sequence.start_value}",
            f"INCREMENT BY {sequence.increment}",
        ]

        if sequence.minimum_value is not None:
            parts.append(f"MINVALUE {sequence.minimum_value}")
        if sequence.maximum_value is not None:
            parts.append(f"MAXVALUE {sequence.maximum_value}")

        parts.append("CYCLE" if sequence.is_cycling else "NO CYCLE")
        if sequence.cache_size and sequence.cache_size > 0:
            parts.append(f"CACHE {sequence.cache_size}")
        else:
            parts.append("NO CACHE")

        parts[-1] += ";"
        return "\n".join(parts) + "\nGO"
