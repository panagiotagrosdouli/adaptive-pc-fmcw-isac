"""Versioned Stage-1 geometry configuration loader."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from iscai_stage1.contracts.stage1a import (
    ARTIFACT_SEMANTICS,
    HeadlampSurrogateConfig,
    ReceiverGeometryConfig,
)


@dataclass(frozen=True)
class Stage1Config:
    schema_version: int
    artifact_semantics: str
    headlamp: HeadlampSurrogateConfig
    receiver: ReceiverGeometryConfig


def _vec3(value: Any, *, name: str) -> tuple[float, float, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{name} must contain exactly three values.")
    return (float(value[0]), float(value[1]), float(value[2]))


def load_stage1_config(path: str | Path) -> Stage1Config:
    """Load and validate the public Stage-1 geometry contract."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if int(payload.get("schema_version", -1)) != 1:
        raise ValueError("Unsupported Stage-1 configuration schema_version.")
    if payload.get("artifact_semantics") != ARTIFACT_SEMANTICS:
        raise ValueError("Stage-1 artifact semantics do not match the contract.")

    headlamp_payload = payload["headlamp"]
    receiver_payload = payload["receiver"]
    covariance_rows = receiver_payload["offset_covariance_body_m2"]
    if not isinstance(covariance_rows, list) or len(covariance_rows) != 3:
        raise ValueError("Receiver covariance must contain three rows.")

    headlamp = HeadlampSurrogateConfig(
        mode=str(headlamp_payload["mode"]),
        longitudinal_inset_m=float(headlamp_payload["longitudinal_inset_m"]),
        lateral_offset_m=float(headlamp_payload["lateral_offset_m"]),
        vertical_offset_m=float(headlamp_payload["vertical_offset_m"]),
        roll_rad=float(headlamp_payload["roll_rad"]),
        pitch_rad=float(headlamp_payload["pitch_rad"]),
        yaw_rad=float(headlamp_payload["yaw_rad"]),
    )
    receiver = ReceiverGeometryConfig(
        mode=str(receiver_payload["mode"]),
        offset_mean_body_m=_vec3(
            receiver_payload["offset_mean_body_m"],
            name="receiver.offset_mean_body_m",
        ),
        offset_covariance_body_m2=(
            _vec3(covariance_rows[0], name="receiver covariance row 0"),
            _vec3(covariance_rows[1], name="receiver covariance row 1"),
            _vec3(covariance_rows[2], name="receiver covariance row 2"),
        ),
    )
    # Validate parameters independent of any specific scene.
    headlamp.translation_in_sdc_m(1.0)
    receiver.validate()

    return Stage1Config(
        schema_version=1,
        artifact_semantics=ARTIFACT_SEMANTICS,
        headlamp=headlamp,
        receiver=receiver,
    )
