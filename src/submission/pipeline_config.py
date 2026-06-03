"""Pipeline configuration models."""

from __future__ import annotations

import yaml
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuration for the submission pipeline."""

    top_k: int = 100
    enable_audit_log: bool = True
    enable_reports: bool = True
    output_dir: str = "outputs"
    jd_path: str | None = None
    candidates_path: str | None = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> "PipelineConfig":
        """Load configuration from a YAML file."""
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path_obj, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        valid_keys = cls.__annotations__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}

        return cls(**filtered_data)

    def to_yaml(self, path: str | Path) -> None:
        """Save configuration to a YAML file."""
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        with open(path_obj, "w", encoding="utf-8") as f:
            yaml.safe_dump(asdict(self), f, sort_keys=False)
