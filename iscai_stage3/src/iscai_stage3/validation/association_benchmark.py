"""Controlled evaluator for Euclidean versus covariance-aware GNN."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from iscai_stage3.tracking.cartesian import CartesianDetectionFrame
from iscai_stage3.tracking.gnn import build_gnn_tracklets


@dataclass(frozen=True)
class AssociationBenchmarkResult:
    metric: str
    associated_edges: int
    correct_edges: int
    association_accuracy: float
    tracklet_count: int


def evaluate_gnn_association(
    frames: tuple[CartesianDetectionFrame, ...],
    *,
    evaluator_identity_by_detection_key: Mapping[str, str],
    association_metric: str,
    chi_square_gate: float = 11.3448667301,
    euclidean_gate_m: float = 5.0,
) -> AssociationBenchmarkResult:
    """Score consecutive links; identities never enter the tracker."""

    tracklets = build_gnn_tracklets(
        frames,
        association_metric=association_metric,  # type: ignore[arg-type]
        chi_square_gate=chi_square_gate,
        euclidean_gate_m=euclidean_gate_m,
    )
    correct = 0
    edges = 0
    for tracklet in tracklets:
        identities = []
        for key in tracklet.source_detection_keys:
            if key not in evaluator_identity_by_detection_key:
                raise KeyError(f"Missing evaluator identity for {key}.")
            identities.append(evaluator_identity_by_detection_key[key])
        for previous, current in zip(identities, identities[1:]):
            edges += 1
            correct += int(previous == current)
    accuracy = correct / edges if edges else 0.0
    return AssociationBenchmarkResult(
        metric=association_metric,
        associated_edges=edges,
        correct_edges=correct,
        association_accuracy=accuracy,
        tracklet_count=len(tracklets),
    )
