"""Persistence helpers for JD analysis artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jd_parser.jd_models import JDAnalysis


class JDFeatureStore:
    """Save and load JDAnalysis objects as JSON or YAML."""

    def save_json(self, analysis: JDAnalysis, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(analysis.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    def load_json(self, path: str | Path) -> JDAnalysis:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("JD analysis JSON must contain an object")
        return JDAnalysis.from_dict(payload)

    def save_yaml(self, analysis: JDAnalysis, path: str | Path) -> None:
        yaml = _load_yaml()
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(yaml.safe_dump(analysis.to_dict(), sort_keys=True), encoding="utf-8")

    def load_yaml(self, path: str | Path) -> JDAnalysis:
        yaml = _load_yaml()
        payload: Any = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("JD analysis YAML must contain an object")
        return JDAnalysis.from_dict(payload)


def _load_yaml() -> Any:
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("YAML support requires PyYAML. Install dependencies from requirements.txt.") from exc
    return yaml

