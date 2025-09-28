from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class TableColumn:
    name: str
    data_type: str
    character_max_length: Optional[int]
    numeric_precision: Optional[int]
    numeric_scale: Optional[int]
    is_nullable: bool
    column_default: Optional[str]
    is_identity: bool = False

    def sql_type(self) -> str:
        type_upper = self.data_type.upper()
        if type_upper in {"CHAR", "NCHAR", "VARCHAR", "NVARCHAR", "BINARY", "VARBINARY"}:
            length = "MAX" if self.character_max_length in (-1, None) else str(self.character_max_length)
            return f"{type_upper}({length})"
        if type_upper in {"DECIMAL", "NUMERIC"}:
            precision = self.numeric_precision or 18
            scale = self.numeric_scale or 0
            return f"{type_upper}({precision},{scale})"
        if type_upper in {"DATETIME2", "TIME", "DATETIMEOFFSET"} and self.numeric_scale is not None:
            return f"{type_upper}({self.numeric_scale})"
        return type_upper


@dataclass(slots=True)
class TableMetadata:
    schema: str
    name: str
    columns: List[TableColumn] = field(default_factory=list)
    primary_keys: List[str] = field(default_factory=list)
    data: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"[{self.schema}].[{self.name}]"


@dataclass(slots=True)
class ViewMetadata:
    schema: str
    name: str
    definition: str

    @property
    def full_name(self) -> str:
        return f"[{self.schema}].[{self.name}]"


@dataclass(slots=True)
class ProcedureMetadata:
    schema: str
    name: str
    definition: str

    @property
    def full_name(self) -> str:
        return f"[{self.schema}].[{self.name}]"


@dataclass(slots=True)
class FunctionMetadata:
    schema: str
    name: str
    definition: str
    type: str

    @property
    def full_name(self) -> str:
        return f"[{self.schema}].[{self.name}]"


@dataclass(slots=True)
class TriggerMetadata:
    schema: str
    table_schema: str
    table_name: str
    name: str
    definition: str
    is_instead_of: bool

    @property
    def full_name(self) -> str:
        return f"[{self.schema}].[{self.name}]"

    @property
    def parent_full_name(self) -> str:
        return f"[{self.table_schema}].[{self.table_name}]"


@dataclass(slots=True)
class DefaultConstraintMetadata:
    schema: str
    table_name: str
    column_name: str
    name: str
    definition: str
    is_system_named: bool

    @property
    def table_full_name(self) -> str:
        return f"[{self.schema}].[{self.table_name}]"


@dataclass(slots=True)
class CheckConstraintMetadata:
    schema: str
    table_name: str
    name: str
    definition: str
    is_not_trusted: bool
    is_disabled: bool

    @property
    def table_full_name(self) -> str:
        return f"[{self.schema}].[{self.table_name}]"


@dataclass(slots=True)
class ForeignKeyMetadata:
    schema: str
    table_name: str
    name: str
    columns: List[str]
    referenced_schema: str
    referenced_table: str
    referenced_columns: List[str]
    delete_action: str
    update_action: str
    is_not_for_replication: bool
    is_disabled: bool
    is_not_trusted: bool

    @property
    def table_full_name(self) -> str:
        return f"[{self.schema}].[{self.table_name}]"

    @property
    def referenced_full_name(self) -> str:
        return f"[{self.referenced_schema}].[{self.referenced_table}]"


@dataclass(slots=True)
class UniqueConstraintMetadata:
    schema: str
    table_name: str
    name: str
    columns: List[str]
    type_desc: str

    @property
    def table_full_name(self) -> str:
        return f"[{self.schema}].[{self.table_name}]"


@dataclass(slots=True)
class IndexColumnMetadata:
    name: str
    is_descending: bool
    is_included: bool
    ordinal: int


@dataclass(slots=True)
class IndexMetadata:
    schema: str
    table_name: str
    name: str
    type_desc: str
    is_unique: bool
    is_disabled: bool
    filter_definition: Optional[str]
    columns: List[IndexColumnMetadata] = field(default_factory=list)

    @property
    def table_full_name(self) -> str:
        return f"[{self.schema}].[{self.table_name}]"

    @property
    def key_columns(self) -> List[IndexColumnMetadata]:
        return [col for col in sorted(self.columns, key=lambda c: c.ordinal) if not col.is_included]

    @property
    def include_columns(self) -> List[IndexColumnMetadata]:
        return [col for col in sorted(self.columns, key=lambda c: c.ordinal) if col.is_included]


@dataclass(slots=True)
class SequenceMetadata:
    schema: str
    name: str
    data_type: str
    start_value: int
    increment: int
    minimum_value: Optional[int]
    maximum_value: Optional[int]
    is_cycling: bool
    cache_size: Optional[int]

    @property
    def full_name(self) -> str:
        return f"[{self.schema}].[{self.name}]"


@dataclass(slots=True)
class SynonymMetadata:
    schema: str
    name: str
    base_object_name: str

    @property
    def full_name(self) -> str:
        return f"[{self.schema}].[{self.name}]"


@dataclass(slots=True)
class UserDefinedTypeMetadata:
    schema: str
    name: str
    underlying_system_type: str
    max_length: Optional[int]
    precision: Optional[int]
    scale: Optional[int]
    is_nullable: bool

    @property
    def full_name(self) -> str:
        return f"[{self.schema}].[{self.name}]"


@dataclass(slots=True)
class TableTypeColumnMetadata:
    name: str
    data_type: str
    character_max_length: Optional[int]
    numeric_precision: Optional[int]
    numeric_scale: Optional[int]
    is_nullable: bool
    is_identity: bool
    column_default: Optional[str]


@dataclass(slots=True)
class TableTypeMetadata:
    schema: str
    name: str
    columns: List[TableTypeColumnMetadata] = field(default_factory=list)
    primary_keys: List[str] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"[{self.schema}].[{self.name}]"


@dataclass(slots=True)
class DatabaseMetadata:
    tables: List[TableMetadata] = field(default_factory=list)
    views: List[ViewMetadata] = field(default_factory=list)
    procedures: List[ProcedureMetadata] = field(default_factory=list)
    functions: List[FunctionMetadata] = field(default_factory=list)
    triggers: List[TriggerMetadata] = field(default_factory=list)
    default_constraints: List[DefaultConstraintMetadata] = field(default_factory=list)
    check_constraints: List[CheckConstraintMetadata] = field(default_factory=list)
    foreign_keys: List[ForeignKeyMetadata] = field(default_factory=list)
    unique_constraints: List[UniqueConstraintMetadata] = field(default_factory=list)
    indexes: List[IndexMetadata] = field(default_factory=list)
    sequences: List[SequenceMetadata] = field(default_factory=list)
    synonyms: List[SynonymMetadata] = field(default_factory=list)
    user_defined_types: List[UserDefinedTypeMetadata] = field(default_factory=list)
    table_types: List[TableTypeMetadata] = field(default_factory=list)
    schemas: List[str] = field(default_factory=list)
