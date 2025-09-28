from __future__ import annotations

import os

import pyodbc


def main() -> None:
    password = os.environ.get("SQLSERVER_PASSWORD", "")
    conn = pyodbc.connect(
        ";".join(
            [
                "DRIVER={ODBC Driver 18 for SQL Server}",
                "SERVER=184.168.30.175,1433",
                "DATABASE=BncplDB",
                "UID=sa",
                f"PWD={password}",
                "Encrypt=no",
                "TrustServerCertificate=yes",
            ]
        )
    )
    cursor = conn.cursor()

    rows = cursor.execute(
        "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES ORDER BY TABLE_SCHEMA, TABLE_NAME"
    ).fetchall()

    sys_tables = cursor.execute(
        "SELECT SCHEMA_NAME(schema_id) AS schema_name, name, is_ms_shipped, temporal_type, is_memory_optimized "
        "FROM sys.tables ORDER BY schema_name, name"
    ).fetchall()

    base_tables = [row for row in rows if row.TABLE_TYPE == "BASE TABLE"]
    non_base = [row for row in rows if row.TABLE_TYPE != "BASE TABLE"]

    print(f"Total objetos: {len(rows)}")
    print(f"Tablas base: {len(base_tables)}")
    print(f"Otras (views, etc.): {len(non_base)}")
    print(f"Total sys.tables (todas): {len(sys_tables)}")

    for row in base_tables:
        print(f"BASE: {row.TABLE_SCHEMA}.{row.TABLE_NAME}")

    if non_base:
        print("\nNo base:")
        for row in non_base:
            print(f"{row.TABLE_TYPE}: {row.TABLE_SCHEMA}.{row.TABLE_NAME}")

    for table in sys_tables:
        if table.is_ms_shipped:
            marker = "[ms]"
        elif table.temporal_type:
            marker = "[temporal]"
        elif table.is_memory_optimized:
            marker = "[memory]"
        else:
            marker = ""
        if marker:
            print(f"SYS: {table.schema_name}.{table.name} {marker}")


if __name__ == "__main__":
    main()
