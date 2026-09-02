from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
from typing import Any


def load_config(path: Path) -> dict[str, Any]:
    """Load a JSON configuration file with explicit validation."""
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON config: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a JSON object: {path}")
    return data


def write_json(path: Path, payload: Any) -> None:
    """Write deterministic, readable JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def resolve_dataset_root(
    config: dict[str, Any],
    override: Path | None = None,
) -> tuple[Path, str]:
    """Resolve data location without embedding a machine-specific path."""
    if override is not None:
        return override.expanduser(), "command_line"

    env_name = str(config.get("dataset_root_env", "WOMD_ROOT"))
    env_value = os.environ.get(env_name)
    if env_value:
        return Path(env_value).expanduser(), f"environment:{env_name}"

    configured = config.get("dataset_root")
    if configured:
        return Path(str(configured)).expanduser(), "config"

    raise ValueError(
        f"Dataset root is unset. Pass --dataset-root or set {env_name}."
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
