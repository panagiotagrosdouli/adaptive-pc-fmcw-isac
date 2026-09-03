#!/usr/bin/env python3
"""Export official WOMD Scenario TFRecords to the canonical Stage-01 NPZ contract.

Requires TensorFlow and Waymo Open Dataset protos. The script uses the true
scenario.sdc_track_index, scenario-level deterministic train/dev ownership,
and strict 11-history/80-future validity for retained vehicle actors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

HISTORY = 11
FUTURE = 80
CURRENT = 10


def stable_dev(scenario_id: str, dev_fraction: float) -> bool:
    value = int(hashlib.sha256(scenario_id.encode()).hexdigest()[:16], 16) / 2**64
    return value < dev_fraction


def rotate_to_sdc(points: np.ndarray, origin: np.ndarray, yaw: float) -> np.ndarray:
    d = points - origin
    c, s = np.cos(yaw), np.sin(yaw)
    # world -> SDC-at-anchor frame
    return np.stack((c * d[..., 0] + s * d[..., 1], -s * d[..., 0] + c * d[..., 1]), -1)


def state_xy(track) -> tuple[np.ndarray, np.ndarray]:
    states = list(track.states)
    xy = np.asarray([[x.center_x, x.center_y] for x in states], dtype=np.float32)
    valid = np.asarray([bool(x.valid) for x in states], dtype=bool)
    return xy, valid


def velocities(history_xy: np.ndarray, dt: float = 0.1) -> np.ndarray:
    out = np.zeros_like(history_xy)
    out[1:] = (history_xy[1:] - history_xy[:-1]) / dt
    out[0] = out[1]
    return out


def export(files: list[Path], output: Path, fixed_split: str | None, dev_fraction: float) -> dict:
    import tensorflow as tf
    from waymo_open_dataset.protos import scenario_pb2

    rows: dict[str, list] = {k: [] for k in (
        "history_xy", "history_vxy", "future_xy", "history_valid", "future_valid",
        "scenario_id", "track_id", "sdc_track_id", "split"
    )}
    scenario_seen: set[str] = set()
    rejected = {"short": 0, "sdc_invalid": 0, "non_vehicle": 0, "invalid_window": 0}

    for file in files:
        for raw in tf.data.TFRecordDataset(str(file)):
            scenario = scenario_pb2.Scenario.FromString(bytes(raw.numpy()))
            sid = str(scenario.scenario_id)
            scenario_seen.add(sid)
            if scenario.current_time_index != CURRENT:
                rejected["short"] += 1
                continue
            tracks = list(scenario.tracks)
            if not (0 <= scenario.sdc_track_index < len(tracks)):
                rejected["sdc_invalid"] += 1
                continue
            sdc = tracks[scenario.sdc_track_index]
            if len(sdc.states) < HISTORY + FUTURE or not sdc.states[CURRENT].valid:
                rejected["sdc_invalid"] += 1
                continue
            anchor = sdc.states[CURRENT]
            origin = np.asarray([anchor.center_x, anchor.center_y], dtype=np.float32)
            yaw = float(anchor.heading)
            sdc_track_id = int(sdc.id)
            split = fixed_split or ("development" if stable_dev(sid, dev_fraction) else "training")

            for track in tracks:
                # WOMD Track.ObjectType.TYPE_VEHICLE == 1.
                if int(track.object_type) != 1:
                    rejected["non_vehicle"] += 1
                    continue
                if len(track.states) < HISTORY + FUTURE:
                    rejected["short"] += 1
                    continue
                xy, valid = state_xy(track)
                h_valid = valid[:HISTORY]
                f_valid = valid[HISTORY:HISTORY + FUTURE]
                if not h_valid.all() or not f_valid.all():
                    rejected["invalid_window"] += 1
                    continue
                h = rotate_to_sdc(xy[:HISTORY], origin, yaw).astype(np.float32)
                f = rotate_to_sdc(xy[HISTORY:HISTORY + FUTURE], origin, yaw).astype(np.float32)
                rows["history_xy"].append(h)
                rows["history_vxy"].append(velocities(h))
                rows["future_xy"].append(f)
                rows["history_valid"].append(h_valid)
                rows["future_valid"].append(f_valid)
                rows["scenario_id"].append(sid)
                rows["track_id"].append(int(track.id))
                rows["sdc_track_id"].append(sdc_track_id)
                rows["split"].append(split)

    if not rows["scenario_id"]:
        raise RuntimeError("No eligible samples were exported.")
    arrays = {
        "history_xy": np.asarray(rows["history_xy"], dtype=np.float32),
        "history_vxy": np.asarray(rows["history_vxy"], dtype=np.float32),
        "future_xy": np.asarray(rows["future_xy"], dtype=np.float32),
        "history_valid": np.asarray(rows["history_valid"], dtype=bool),
        "future_valid": np.asarray(rows["future_valid"], dtype=bool),
        "scenario_id": np.asarray(rows["scenario_id"], dtype=str),
        "track_id": np.asarray(rows["track_id"], dtype=np.int64),
        "sdc_track_id": np.asarray(rows["sdc_track_id"], dtype=np.int64),
        "split": np.asarray(rows["split"], dtype=str),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output, **arrays)
    return {
        "output": str(output), "samples": len(arrays["scenario_id"]),
        "source_scenarios": len(scenario_seen), "retained_scenarios": len(set(rows["scenario_id"])),
        "splits": {x: int(np.sum(arrays["split"] == x)) for x in np.unique(arrays["split"])},
        "rejected": rejected, "true_sdc_geometry": True,
        "history_steps": HISTORY, "future_steps": FUTURE,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, nargs="+", required=True, help="TFRecord files or directories")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--fixed-split", choices=["official_validation"])
    p.add_argument("--development-fraction", type=float, default=0.10)
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    if not 0.0 <= args.development_fraction < 1.0:
        p.error("--development-fraction must be in [0,1)")
    files: list[Path] = []
    for item in args.input:
        files.extend(sorted(item.glob("*.tfrecord*")) if item.is_dir() else [item])
    if not files:
        p.error("no TFRecord files found")
    report = export(files, args.output, args.fixed_split, args.development_fraction)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
