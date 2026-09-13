#!/usr/bin/env python3
"""Export the frozen publication action set with derived profile/resource quantities."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from pcfmcw_isac.policy_evaluation import normalized_resource_cost, profile_registry
from pcfmcw_isac.publication_protocol import FROZEN_PROTOCOL_V1
from pcfmcw_isac.publication_validation import _comm_cfg


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/publication/submission/action_space.csv")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    profiles = profile_registry()
    actions = FROZEN_PROTOCOL_V1.actions()
    if len(actions) != 54:
        raise RuntimeError(f"frozen action set changed: expected 54, got {len(actions)}")

    fields = [
        "action_id",
        "profile_name",
        "chips_per_chirp",
        "tx_power_backoff_db",
        "repetition_factor",
        "raw_bit_rate_bps",
        "nominal_rate_after_repetition_bps",
        "normalized_resource_cost",
        "range_resolution_m",
        "positive_if_max_range_m",
        "velocity_resolution_mps",
        "max_unambiguous_velocity_mps",
        "adc_samples_per_frame",
    ]
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for action_id, action in enumerate(actions):
            profile = profiles[action.profile_name]
            cfg = _comm_cfg(action.profile_name, action.chips_per_chirp)
            writer.writerow(
                {
                    "action_id": action_id,
                    "profile_name": action.profile_name,
                    "chips_per_chirp": action.chips_per_chirp,
                    "tx_power_backoff_db": action.tx_power_backoff_db,
                    "repetition_factor": action.repetition_factor,
                    "raw_bit_rate_bps": cfg.raw_bit_rate_bps,
                    "nominal_rate_after_repetition_bps": cfg.raw_bit_rate_bps / action.repetition_factor,
                    "normalized_resource_cost": normalized_resource_cost(action),
                    "range_resolution_m": profile.range_resolution_m,
                    "positive_if_max_range_m": profile.positive_if_max_range_m,
                    "velocity_resolution_mps": profile.velocity_resolution_mps,
                    "max_unambiguous_velocity_mps": profile.max_unambiguous_velocity_mps,
                    "adc_samples_per_frame": profile.samples_per_chirp * profile.n_chirps,
                }
            )

    print(f"wrote {len(actions)} actions to {output}")


if __name__ == "__main__":
    main()
