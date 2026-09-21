"""Reproducible experiment-grid utilities for publication runs."""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Iterable

from .publication_protocol import (
    EvaluationState,
    FrozenPublicationProtocol,
    FROZEN_PROTOCOL_V1,
)


def publication_states(
    *,
    protocol: FrozenPublicationProtocol = FROZEN_PROTOCOL_V1,
    seeds: Iterable[int] | None = None,
) -> Iterable[EvaluationState]:
    """Yield states from the frozen publication protocol.

    Final evaluation should use the default seed family. Tests/pilot smoke runs
    may provide an explicit small seed iterable, but their outputs must not be
    mixed with frozen final statistics.
    """
    protocol.validate()
    return protocol.states(seeds=seeds)


def write_manifest(
    points: Iterable[EvaluationState],
    path: str | Path,
    *,
    protocol: FrozenPublicationProtocol = FROZEN_PROTOCOL_V1,
) -> None:
    """Write a machine-readable experiment manifest with protocol metadata."""
    protocol.validate()
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "protocol_id": protocol.protocol_id,
        "qos": asdict(protocol.qos),
        "final_seed_start": protocol.final_seed_start,
        "n_final_seeds": protocol.n_final_seeds,
        "bootstrap_confidence": protocol.bootstrap_confidence,
        "bootstrap_resamples": protocol.bootstrap_resamples,
        "states": [asdict(x) for x in points],
    }
    p.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
