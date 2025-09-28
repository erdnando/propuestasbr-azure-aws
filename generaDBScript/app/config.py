from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import os

import yaml
from pydantic import BaseModel, Field, model_validator


ENV_VAR_PATTERN = "${"  # marker used to detect environment variables in YAML values


def _expand_env_vars(value: Any) -> Any:
    """Recursively replace ${VAR} patterns with environment variables."""

    if isinstance(value, str) and ENV_VAR_PATTERN in value:
        return os.path.expandvars(value)

    if isinstance(value, list):
        return [_expand_env_vars(item) for item in value]

    if isinstance(value, dict):
        return {key: _expand_env_vars(val) for key, val in value.items()}

    return value


class DatabaseConfig(BaseModel):
    server: str
    database: str
    username: str
    password: str
    port: int = 1433
    encrypt: bool = True
    trust_server_certificate: bool = True
    schema: str = "dbo"
    include_tables: Optional[List[str]] = Field(default=None, description="Lista opcional de tablas a incluir")
    include_views: Optional[List[str]] = Field(default=None, description="Lista opcional de vistas a incluir")
    include_procedures: Optional[List[str]] = Field(default=None, description="Lista opcional de stored procedures a incluir")
    include_functions: Optional[List[str]] = Field(default=None, description="Lista opcional de funciones definidas por el usuario")
    include_triggers: Optional[List[str]] = Field(default=None, description="Lista opcional de triggers a incluir")
    include_sequences: Optional[List[str]] = Field(default=None, description="Lista opcional de secuencias a incluir")
    include_synonyms: Optional[List[str]] = Field(default=None, description="Lista opcional de sinónimos a incluir")
    include_table_types: Optional[List[str]] = Field(default=None, description="Lista opcional de tipos de tabla a incluir")
    include_user_types: Optional[List[str]] = Field(default=None, description="Lista opcional de tipos escalares definidos por el usuario")

    odbc_driver: str = Field(default="ODBC Driver 18 for SQL Server", alias="driver")

    @model_validator(mode="before")
    @classmethod
    def _expand_envars(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        return _expand_env_vars(data)

    @property
    def quoted_schema(self) -> str:
        return f"[{self.schema}]"

    def connection_string(self) -> str:
        parts = [
            f"DRIVER={{{self.odbc_driver}}}",
            f"SERVER={self.server},{self.port}",
            f"DATABASE={self.database}",
            f"UID={self.username}",
            f"PWD={self.password}",
            f"Encrypt={'yes' if self.encrypt else 'no'}",
            f"TrustServerCertificate={'yes' if self.trust_server_certificate else 'no'}",
        ]
        return ";".join(parts)


class OutputConfig(BaseModel):
    directory: Path = Field(default=Path("output"))
    include_data: bool = True
    rows_per_table: Optional[int] = Field(default=None, description="Número máximo de filas por tabla para los inserts")
    batch_size: int = Field(default=5000, description="Número de filas a procesar por lote durante la extracción de datos")
    include_default_constraints: bool = True
    include_check_constraints: bool = True
    include_foreign_keys: bool = True
    include_unique_constraints: bool = True
    include_indexes: bool = True
    include_functions: bool = True
    include_triggers: bool = True
    include_sequences: bool = True
    include_synonyms: bool = True
    include_user_types: bool = True
    include_table_types: bool = True

    @model_validator(mode="before")
    @classmethod
    def _normalize_directory(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(data, dict) and "directory" in data:
            data = data.copy()
            data["directory"] = Path(data["directory"])
        return data


class AppConfig(BaseModel):
    database: DatabaseConfig
    output: OutputConfig

    @classmethod
    def from_file(cls, path: Path) -> "AppConfig":
        with path.open("r", encoding="utf-8") as fh:
            payload = yaml.safe_load(fh) or {}
        payload = _expand_env_vars(payload)
        return cls(**payload)

    def merge_overrides(self, overrides: Dict[str, Any]) -> None:
        if not overrides:
            return
        if "database" in overrides:
            self.database = self.database.model_copy(update=overrides["database"])
        if "output" in overrides:
            self.output = self.output.model_copy(update=overrides["output"])

    def ensure_output_dir(self) -> Path:
        self.output.directory.mkdir(parents=True, exist_ok=True)
        return self.output.directory

    def __str__(self) -> str:
        return (
            f"Database: {self.database.server}/{self.database.database} schema={self.database.schema}\n"
            f"Output: {self.output.directory} include_data={self.output.include_data}"
        )


def build_config(config_path: Optional[Path], overrides: Optional[Dict[str, Any]] = None) -> AppConfig:
    if config_path is None:
        raise ValueError("Se requiere un archivo de configuración o parámetros de conexión")

    config = AppConfig.from_file(config_path)
    config.merge_overrides(overrides or {})
    return config
