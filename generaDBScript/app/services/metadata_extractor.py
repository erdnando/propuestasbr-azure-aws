from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import pyodbc

from app.config import DatabaseConfig
from app.models import (
    CheckConstraintMetadata,
    DatabaseMetadata,
    DefaultConstraintMetadata,
    ForeignKeyMetadata,
    FunctionMetadata,
    IndexColumnMetadata,
    IndexMetadata,
    ProcedureMetadata,
    SequenceMetadata,
    SynonymMetadata,
    TableColumn,
    TableMetadata,
    TableTypeColumnMetadata,
    TableTypeMetadata,
    TriggerMetadata,
    UniqueConstraintMetadata,
    UserDefinedTypeMetadata,
    ViewMetadata,
)


class MetadataExtractor:
    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config

    def _connect(self) -> pyodbc.Connection:
        return pyodbc.connect(self._config.connection_string())

    def extract(self) -> DatabaseMetadata:
        with self._connect() as conn:
            include_tables = self._split_includes(self._config.include_tables)
            table_identifiers = self._fetch_tables(conn, include_tables)
            columns_map = self._fetch_columns(conn, table_identifiers)
            pk_map = self._fetch_primary_keys(conn, table_identifiers)

            tables: List[TableMetadata] = []
            for schema, table_name in table_identifiers:
                columns = columns_map.get((schema, table_name), [])
                tables.append(
                    TableMetadata(
                        schema=schema,
                        name=table_name,
                        columns=columns,
                        primary_keys=pk_map.get((schema, table_name), []),
                    )
                )

            views = self._fetch_views(conn, self._split_includes(self._config.include_views))
            procedures = self._fetch_procedures(conn, self._split_includes(self._config.include_procedures))
            functions = self._fetch_functions(conn, self._split_includes(self._config.include_functions))
            triggers = self._fetch_triggers(conn, self._split_includes(self._config.include_triggers))

            default_constraints = self._fetch_default_constraints(conn, include_tables)
            check_constraints = self._fetch_check_constraints(conn, include_tables)
            foreign_keys = self._fetch_foreign_keys(conn, include_tables)
            unique_constraints = self._fetch_unique_constraints(conn, include_tables)
            indexes = self._fetch_indexes(conn, include_tables)

            sequences = self._fetch_sequences(conn, self._split_includes(self._config.include_sequences))
            synonyms = self._fetch_synonyms(conn, self._split_includes(self._config.include_synonyms))
            user_types = self._fetch_user_defined_types(conn, self._split_includes(self._config.include_user_types))
            table_types = self._fetch_table_types(conn, self._split_includes(self._config.include_table_types))

            schema_names = sorted(
                {table.schema for table in tables}
                | {view.schema for view in views}
                | {proc.schema for proc in procedures}
                | {fn.schema for fn in functions}
                | {tr.schema for tr in triggers}
                | {seq.schema for seq in sequences}
                | {syn.schema for syn in synonyms}
                | {tp.schema for tp in table_types}
                | {ut.schema for ut in user_types}
            )

        return DatabaseMetadata(
            tables=tables,
            views=views,
            procedures=procedures,
            functions=functions,
            triggers=triggers,
            default_constraints=default_constraints,
            check_constraints=check_constraints,
            foreign_keys=foreign_keys,
            unique_constraints=unique_constraints,
            indexes=indexes,
            sequences=sequences,
            synonyms=synonyms,
            user_defined_types=user_types,
            table_types=table_types,
            schemas=schema_names,
        )

    @staticmethod
    def _split_includes(includes: Optional[Sequence[str]]) -> Tuple[set[Tuple[str, str]], set[str]]:
        with_schema: set[Tuple[str, str]] = set()
        without_schema: set[str] = set()
        if not includes:
            return with_schema, without_schema

        for item in includes:
            if "." in item:
                schema, name = item.split(".", 1)
                with_schema.add((schema, name))
            else:
                without_schema.add(item)
        return with_schema, without_schema

    @staticmethod
    def _should_include(
        schema: str,
        name: str,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> bool:
        with_schema, without_schema = includes
        if not with_schema and not without_schema:
            return True
        if (schema, name) in with_schema:
            return True
        return name in without_schema

    def _fetch_tables(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[Tuple[str, str]]:
        cursor = conn.cursor()
        base_query = (
            "SELECT TABLE_SCHEMA, TABLE_NAME "
            "FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_TYPE = 'BASE TABLE' "
        )
        params: List[str] = []
        filters: List[str] = []

        if self._config.schema:
            filters.append("TABLE_SCHEMA = ?")
            params.append(self._config.schema)

        if filters:
            base_query += " AND " + " AND ".join(filters)

        base_query += " ORDER BY TABLE_SCHEMA, TABLE_NAME"

        rows = cursor.execute(base_query, params).fetchall()
        return [
            (row.TABLE_SCHEMA, row.TABLE_NAME)
            for row in rows
            if self._should_include(row.TABLE_SCHEMA, row.TABLE_NAME, includes)
        ]

    def _fetch_columns(
        self,
        conn: pyodbc.Connection,
        tables: Iterable[Tuple[str, str]],
    ) -> Dict[Tuple[str, str], List[TableColumn]]:
        table_list = list(tables)
        if not table_list:
            return {}

        cursor = conn.cursor()
        schema_placeholders = ",".join("?" for _ in table_list)
        query = (
            "SELECT c.TABLE_SCHEMA, c.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE, "
            "c.CHARACTER_MAXIMUM_LENGTH, c.NUMERIC_PRECISION, c.NUMERIC_SCALE, c.IS_NULLABLE, "
            "COLUMNPROPERTY(object_id(QUOTENAME(c.TABLE_SCHEMA) + '.' + QUOTENAME(c.TABLE_NAME)), c.COLUMN_NAME, 'IsIdentity') AS IS_IDENTITY, "
            "c.ORDINAL_POSITION "
            "FROM INFORMATION_SCHEMA.COLUMNS c "
            "JOIN (VALUES "
        )

        values_clause = []
        params: List[str] = []
        for schema, table_name in table_list:
            values_clause.append("(?, ?)")
            params.extend([schema, table_name])
        query += ",".join(values_clause)
        query += (
            ") AS t(schema_name, table_name) "
            "ON c.TABLE_SCHEMA = t.schema_name AND c.TABLE_NAME = t.table_name "
            "ORDER BY c.TABLE_SCHEMA, c.TABLE_NAME, c.ORDINAL_POSITION"
        )

        rows = cursor.execute(query, params).fetchall()

        grouped: Dict[Tuple[str, str], List[TableColumn]] = defaultdict(list)
        for row in rows:
            grouped[(row.TABLE_SCHEMA, row.TABLE_NAME)].append(
                TableColumn(
                    name=row.COLUMN_NAME,
                    data_type=row.DATA_TYPE,
                    character_max_length=row.CHARACTER_MAXIMUM_LENGTH,
                    numeric_precision=row.NUMERIC_PRECISION,
                    numeric_scale=row.NUMERIC_SCALE,
                    is_nullable=row.IS_NULLABLE == "YES",
                    column_default=None,
                    is_identity=bool(row.IS_IDENTITY),
                )
            )
        return grouped

    def _fetch_primary_keys(
        self,
        conn: pyodbc.Connection,
        tables: Iterable[Tuple[str, str]],
    ) -> Dict[Tuple[str, str], List[str]]:
        table_list = list(tables)
        if not table_list:
            return {}

        cursor = conn.cursor()
        values_clause = []
        params: List[str] = []
        for schema, table_name in table_list:
            values_clause.append("(?, ?)")
            params.extend([schema, table_name])

        query = (
            "SELECT kcu.TABLE_SCHEMA, kcu.TABLE_NAME, kcu.COLUMN_NAME "
            "FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc "
            "JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu "
            "ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME "
            "AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA "
            "AND tc.TABLE_NAME = kcu.TABLE_NAME "
            "JOIN (VALUES "
            + ",".join(values_clause)
            + ") AS src(schema_name, table_name) "
            "ON kcu.TABLE_SCHEMA = src.schema_name AND kcu.TABLE_NAME = src.table_name "
            "WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY' "
            "ORDER BY kcu.TABLE_SCHEMA, kcu.TABLE_NAME, kcu.ORDINAL_POSITION"
        )

        rows = cursor.execute(query, params).fetchall()
        grouped: Dict[Tuple[str, str], List[str]] = defaultdict(list)
        for row in rows:
            grouped[(row.TABLE_SCHEMA, row.TABLE_NAME)].append(row.COLUMN_NAME)
        return grouped

    def stream_table_rows(
        self,
        table: TableMetadata,
        rows_per_table: Optional[int],
        batch_size: int,
    ) -> Iterable[List[Dict[str, object]]]:
        connection = self._connect()
        try:
            cursor = connection.cursor()
            column_list = ", ".join(f"[{col.name}]" for col in table.columns)
            select_prefix = "SELECT"
            if rows_per_table and rows_per_table > 0:
                select_prefix = f"SELECT TOP {rows_per_table}"
            query = f"{select_prefix} {column_list} FROM {table.full_name}"
            cursor.execute(query)

            column_names = [col.name for col in table.columns]
            fetched = 0
            while True:
                batch = cursor.fetchmany(batch_size)
                if not batch:
                    break
                fetched += len(batch)
                yield [
                    {column: getattr(row, column) for column in column_names}
                    for row in batch
                ]
                if rows_per_table and rows_per_table > 0 and fetched >= rows_per_table:
                    break
        finally:
            connection.close()

    def _fetch_views(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[ViewMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT s.name AS schema_name, v.name, m.definition "
            "FROM sys.views v "
            "JOIN sys.schemas s ON v.schema_id = s.schema_id "
            "JOIN sys.sql_modules m ON v.object_id = m.object_id "
            "WHERE v.is_ms_shipped = 0"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, v.name"

        rows = cursor.execute(query, params).fetchall()
        return [
            ViewMetadata(schema=row.schema_name, name=row.name, definition=row.definition)
            for row in rows
            if row.definition and self._should_include(row.schema_name, row.name, includes)
        ]

    def _fetch_procedures(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[ProcedureMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT s.name AS schema_name, p.name, m.definition "
            "FROM sys.procedures p "
            "JOIN sys.schemas s ON p.schema_id = s.schema_id "
            "JOIN sys.sql_modules m ON p.object_id = m.object_id "
            "WHERE p.is_ms_shipped = 0"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, p.name"

        rows = cursor.execute(query, params).fetchall()
        return [
            ProcedureMetadata(schema=row.schema_name, name=row.name, definition=row.definition)
            for row in rows
            if row.definition and self._should_include(row.schema_name, row.name, includes)
        ]

    def _fetch_functions(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[FunctionMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT s.name AS schema_name, o.name, o.type, m.definition "
            "FROM sys.objects o "
            "JOIN sys.schemas s ON o.schema_id = s.schema_id "
            "LEFT JOIN sys.sql_modules m ON o.object_id = m.object_id "
            "WHERE o.type IN ('FN','IF','TF','FS','FT') AND o.is_ms_shipped = 0"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, o.name"

        rows = cursor.execute(query, params).fetchall()
        return [
            FunctionMetadata(schema=row.schema_name, name=row.name, type=row.type, definition=row.definition)
            for row in rows
            if row.definition and self._should_include(row.schema_name, row.name, includes)
        ]

    def _fetch_triggers(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[TriggerMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT ts.name AS table_schema, tbl.name AS table_name, s.name AS trigger_schema, tr.name, tr.is_instead_of_trigger, m.definition "
            "FROM sys.triggers tr "
            "JOIN sys.objects tbl ON tr.parent_id = tbl.object_id "
            "JOIN sys.schemas ts ON tbl.schema_id = ts.schema_id "
            "JOIN sys.objects tro ON tr.object_id = tro.object_id "
            "JOIN sys.schemas s ON tro.schema_id = s.schema_id "
            "LEFT JOIN sys.sql_modules m ON tr.object_id = m.object_id "
            "WHERE tr.is_ms_shipped = 0 AND tr.parent_class = 1"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND ts.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY ts.name, tbl.name, tr.name"

        rows = cursor.execute(query, params).fetchall()
        return [
            TriggerMetadata(
                schema=row.trigger_schema,
                table_schema=row.table_schema,
                table_name=row.table_name,
                name=row.name,
                definition=row.definition,
                is_instead_of=bool(row.is_instead_of_trigger),
            )
            for row in rows
            if row.definition and self._should_include(row.trigger_schema, row.name, includes)
        ]

    def _fetch_default_constraints(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[DefaultConstraintMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT s.name AS schema_name, t.name AS table_name, c.name AS column_name, dc.name, dc.definition, dc.is_system_named "
            "FROM sys.default_constraints dc "
            "JOIN sys.columns c ON dc.parent_object_id = c.object_id AND dc.parent_column_id = c.column_id "
            "JOIN sys.tables t ON c.object_id = t.object_id "
            "JOIN sys.schemas s ON t.schema_id = s.schema_id "
            "WHERE t.is_ms_shipped = 0"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, t.name, c.column_id"

        rows = cursor.execute(query, params).fetchall()
        return [
            DefaultConstraintMetadata(
                schema=row.schema_name,
                table_name=row.table_name,
                column_name=row.column_name,
                name=row.name,
                definition=row.definition,
                is_system_named=bool(row.is_system_named),
            )
            for row in rows
            if row.definition and self._should_include(row.schema_name, row.table_name, includes)
        ]

    def _fetch_check_constraints(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[CheckConstraintMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT s.name AS schema_name, t.name AS table_name, cc.name, cc.definition, cc.is_not_trusted, cc.is_disabled "
            "FROM sys.check_constraints cc "
            "JOIN sys.tables t ON cc.parent_object_id = t.object_id "
            "JOIN sys.schemas s ON t.schema_id = s.schema_id "
            "WHERE t.is_ms_shipped = 0"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, t.name, cc.name"

        rows = cursor.execute(query, params).fetchall()
        return [
            CheckConstraintMetadata(
                schema=row.schema_name,
                table_name=row.table_name,
                name=row.name,
                definition=row.definition,
                is_not_trusted=bool(row.is_not_trusted),
                is_disabled=bool(row.is_disabled),
            )
            for row in rows
            if row.definition and self._should_include(row.schema_name, row.table_name, includes)
        ]

    def _fetch_foreign_keys(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[ForeignKeyMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT fk.name, s.name AS schema_name, t.name AS table_name, rs.name AS ref_schema, rt.name AS ref_table, "
            "fk.delete_referential_action_desc, fk.update_referential_action_desc, fk.is_not_for_replication, fk.is_disabled, fk.is_not_trusted, fk.object_id "
            "FROM sys.foreign_keys fk "
            "JOIN sys.tables t ON fk.parent_object_id = t.object_id "
            "JOIN sys.schemas s ON t.schema_id = s.schema_id "
            "JOIN sys.tables rt ON fk.referenced_object_id = rt.object_id "
            "JOIN sys.schemas rs ON rt.schema_id = rs.schema_id "
            "WHERE fk.is_ms_shipped = 0"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, t.name, fk.name"

        rows = cursor.execute(query, params).fetchall()

        result: List[ForeignKeyMetadata] = []
        for row in rows:
            if not self._should_include(row.schema_name, row.table_name, includes):
                continue
            column_rows = cursor.execute(
                "SELECT pc.name AS parent_column, rc.name AS referenced_column "
                "FROM sys.foreign_key_columns fkc "
                "JOIN sys.columns pc ON fkc.parent_object_id = pc.object_id AND fkc.parent_column_id = pc.column_id "
                "JOIN sys.columns rc ON fkc.referenced_object_id = rc.object_id AND fkc.referenced_column_id = rc.column_id "
                "WHERE fkc.constraint_object_id = ? ORDER BY fkc.constraint_column_id",
                row.object_id,
            ).fetchall()
            parent_columns = [col.parent_column for col in column_rows]
            referenced_columns = [col.referenced_column for col in column_rows]
            result.append(
                ForeignKeyMetadata(
                    schema=row.schema_name,
                    table_name=row.table_name,
                    name=row.name,
                    columns=parent_columns,
                    referenced_schema=row.ref_schema,
                    referenced_table=row.ref_table,
                    referenced_columns=referenced_columns,
                    delete_action=row.delete_referential_action_desc,
                    update_action=row.update_referential_action_desc,
                    is_not_for_replication=bool(row.is_not_for_replication),
                    is_disabled=bool(row.is_disabled),
                    is_not_trusted=bool(row.is_not_trusted),
                )
            )
        return result

    def _fetch_unique_constraints(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[UniqueConstraintMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT kc.name, s.name AS schema_name, t.name AS table_name, i.type_desc, kc.unique_index_id, kc.parent_object_id "
            "FROM sys.key_constraints kc "
            "JOIN sys.tables t ON kc.parent_object_id = t.object_id "
            "JOIN sys.schemas s ON t.schema_id = s.schema_id "
            "JOIN sys.indexes i ON kc.parent_object_id = i.object_id AND kc.unique_index_id = i.index_id "
            "WHERE kc.type IN ('UQ','UK') AND kc.is_ms_shipped = 0"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, t.name, kc.name"

        rows = cursor.execute(query, params).fetchall()
        results: List[UniqueConstraintMetadata] = []
        for row in rows:
            if not self._should_include(row.schema_name, row.table_name, includes):
                continue
            column_rows = cursor.execute(
                "SELECT c.name AS column_name "
                "FROM sys.index_columns ic "
                "JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id "
                "WHERE ic.object_id = ? AND ic.index_id = ? AND ic.is_included_column = 0 "
                "ORDER BY ic.key_ordinal",
                row.parent_object_id,
                row.unique_index_id,
            ).fetchall()
            results.append(
                UniqueConstraintMetadata(
                    schema=row.schema_name,
                    table_name=row.table_name,
                    name=row.name,
                    columns=[col.column_name for col in column_rows],
                    type_desc=row.type_desc,
                )
            )
        return results

    def _fetch_indexes(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[IndexMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT i.object_id, i.index_id, i.name, i.type_desc, i.is_unique, i.is_disabled, i.filter_definition, s.name AS schema_name, t.name AS table_name "
            "FROM sys.indexes i "
            "JOIN sys.tables t ON i.object_id = t.object_id "
            "JOIN sys.schemas s ON t.schema_id = s.schema_id "
            "WHERE i.is_hypothetical = 0 AND i.is_primary_key = 0 AND i.is_unique_constraint = 0 AND i.name IS NOT NULL"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, t.name, i.index_id"

        rows = cursor.execute(query, params).fetchall()
        results: List[IndexMetadata] = []
        for row in rows:
            if not self._should_include(row.schema_name, row.table_name, includes):
                continue
            column_rows = cursor.execute(
                "SELECT c.name AS column_name, ic.is_descending_key, ic.is_included_column, ic.key_ordinal, ic.index_column_id "
                "FROM sys.index_columns ic "
                "JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id "
                "WHERE ic.object_id = ? AND ic.index_id = ? "
                "ORDER BY CASE WHEN ic.is_included_column = 1 THEN 1 ELSE 0 END, ic.key_ordinal, ic.index_column_id",
                row.object_id,
                row.index_id,
            ).fetchall()
            columns: List[IndexColumnMetadata] = []
            include_counter = 0
            for col in column_rows:
                key_ordinal = int(col.key_ordinal or 0)
                ordinal = key_ordinal if key_ordinal > 0 else 1000 + include_counter
                columns.append(
                    IndexColumnMetadata(
                        name=col.column_name,
                        is_descending=bool(col.is_descending_key),
                        is_included=bool(col.is_included_column),
                        ordinal=ordinal,
                    )
                )
                if bool(col.is_included_column):
                    include_counter += 1
            results.append(
                IndexMetadata(
                    schema=row.schema_name,
                    table_name=row.table_name,
                    name=row.name,
                    type_desc=row.type_desc,
                    is_unique=bool(row.is_unique),
                    is_disabled=bool(row.is_disabled),
                    filter_definition=row.filter_definition,
                    columns=columns,
                )
            )
        return results

    def _fetch_sequences(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[SequenceMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT s.name AS schema_name, seq.name, TYPE_NAME(seq.user_type_id) AS data_type, seq.start_value, seq.increment, seq.minimum_value, seq.maximum_value, seq.is_cycling, seq.cache_size "
            "FROM sys.sequences seq "
            "JOIN sys.schemas s ON seq.schema_id = s.schema_id"
        )
        params: List[str] = []
        if self._config.schema:
            query += " WHERE s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, seq.name"

        rows = cursor.execute(query, params).fetchall()
        return [
            SequenceMetadata(
                schema=row.schema_name,
                name=row.name,
                data_type=row.data_type,
                start_value=row.start_value,
                increment=row.increment,
                minimum_value=row.minimum_value,
                maximum_value=row.maximum_value,
                is_cycling=bool(row.is_cycling),
                cache_size=row.cache_size,
            )
            for row in rows
            if self._should_include(row.schema_name, row.name, includes)
        ]

    def _fetch_synonyms(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[SynonymMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT s.name AS schema_name, syn.name, syn.base_object_name "
            "FROM sys.synonyms syn "
            "JOIN sys.schemas s ON syn.schema_id = s.schema_id"
        )
        params: List[str] = []
        if self._config.schema:
            query += " WHERE s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, syn.name"

        rows = cursor.execute(query, params).fetchall()
        return [
            SynonymMetadata(schema=row.schema_name, name=row.name, base_object_name=row.base_object_name)
            for row in rows
            if self._should_include(row.schema_name, row.name, includes)
        ]

    def _fetch_user_defined_types(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[UserDefinedTypeMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT s.name AS schema_name, t.name, TYPE_NAME(t.system_type_id) AS base_type, t.max_length, t.precision, t.scale, t.is_nullable "
            "FROM sys.types t "
            "JOIN sys.schemas s ON t.schema_id = s.schema_id "
            "WHERE t.is_user_defined = 1 AND t.is_table_type = 0"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, t.name"

        rows = cursor.execute(query, params).fetchall()
        return [
            UserDefinedTypeMetadata(
                schema=row.schema_name,
                name=row.name,
                underlying_system_type=row.base_type,
                max_length=row.max_length,
                precision=row.precision,
                scale=row.scale,
                is_nullable=bool(row.is_nullable),
            )
            for row in rows
            if self._should_include(row.schema_name, row.name, includes)
        ]

    def _fetch_table_types(
        self,
        conn: pyodbc.Connection,
        includes: Tuple[set[Tuple[str, str]], set[str]],
    ) -> List[TableTypeMetadata]:
        cursor = conn.cursor()
        query = (
            "SELECT s.name AS schema_name, tt.name, tt.type_table_object_id "
            "FROM sys.table_types tt "
            "JOIN sys.schemas s ON tt.schema_id = s.schema_id "
            "WHERE tt.is_user_defined = 1"
        )
        params: List[str] = []
        if self._config.schema:
            query += " AND s.name = ?"
            params.append(self._config.schema)
        query += " ORDER BY s.name, tt.name"

        rows = cursor.execute(query, params).fetchall()
        results: List[TableTypeMetadata] = []
        for row in rows:
            if not self._should_include(row.schema_name, row.name, includes):
                continue
            columns_rows = cursor.execute(
                "SELECT c.name, TYPE_NAME(c.system_type_id) AS data_type, c.max_length, c.precision, c.scale, c.is_nullable, "
                "COLUMNPROPERTY(tt2.type_table_object_id, c.name, 'IsIdentity') AS is_identity, dc.definition "
                "FROM sys.columns c "
                "JOIN sys.table_types tt2 ON c.object_id = tt2.type_table_object_id "
                "LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id "
                "WHERE tt2.type_table_object_id = ? ORDER BY c.column_id",
                row.type_table_object_id,
            ).fetchall()
            columns = []
            for col in columns_rows:
                columns.append(
                    TableTypeColumnMetadata(
                        name=col.name,
                        data_type=col.data_type,
                        character_max_length=col.max_length,
                        numeric_precision=col.precision,
                        numeric_scale=col.scale,
                        is_nullable=bool(col.is_nullable),
                        is_identity=bool(col.is_identity),
                        column_default=col.definition,
                    )
                )
            pk_rows = cursor.execute(
                "SELECT c.name AS column_name "
                "FROM sys.indexes i "
                "JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id "
                "JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id "
                "WHERE i.object_id = ? AND i.is_primary_key = 1 ORDER BY ic.key_ordinal",
                row.type_table_object_id,
            ).fetchall()
            primary_keys = [pk.column_name for pk in pk_rows]
            results.append(
                TableTypeMetadata(
                    schema=row.schema_name,
                    name=row.name,
                    columns=columns,
                    primary_keys=primary_keys,
                )
            )
        return results
