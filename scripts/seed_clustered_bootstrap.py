"""Supplemental *seed-clustered* paired bootstrap for PC-FMCW policy comparisons.

Unlike the frozen primary observation-level bootstrap, this resamples entire
seed groups and preserves the 12 scenario observations within each seed.
It is a sensitivity analysis, not a replacement for the frozen protocol.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def seed_clustered_paired_bootstrap(records, policy_a, policy_b, *, metric="joint_qos",
                                    confidence=0.95, n_resamples=10000, seed=20261012):
    if not (0 < confidence < 1) or n_resamples < 1:
        raise ValueError("invalid bootstrap settings")
    pairs = defaultdict(dict)
    for r in records:
        policy = r["policy"]
        if policy not in {policy_a, policy_b}:
            continue
        key = (int(r["state"]["seed"]), int(r["scenario_id"]))
        if policy in pairs[key]:
            raise ValueError(f"duplicate policy evaluation for {key}")
        pairs[key][policy] = float(r.get(metric, 0.0))
    if not pairs or any(set(v) != {policy_a, policy_b} for v in pairs.values()):
        raise ValueError("missing policy in one or more paired units")

    groups = defaultdict(list)
    for (seed_id, _scenario), observations in pairs.items():
        groups[seed_id].append(observations[policy_a] - observations[policy_b])
    ids = sorted(groups)
    sizes = np.array([len(groups[k]) for k in ids], dtype=float)
    totals = np.array([sum(groups[k]) for k in ids], dtype=float)
    if len(ids) < 2:
        raise ValueError("at least two independent seed clusters required")
    rng = np.random.default_rng(seed)
    # Small batches avoid allocating n_resamples x n_seeds matrices for large studies.
    boots = np.empty(n_resamples)
    for start in range(0, n_resamples, 128):
        end = min(start + 128, n_resamples)
        indices = rng.integers(0, len(ids), size=(end - start, len(ids)))
        boots[start:end] = totals[indices].sum(axis=1) / sizes[indices].sum(axis=1)
    alpha = 1 - confidence
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return {
        "evidence_class": "SUPPLEMENTAL_SEED_CLUSTERED_BOOTSTRAP_NOT_FROZEN_PRIMARY",
        "policy_a": policy_a, "policy_b": policy_b, "metric": metric,
        "n_clusters": len(ids), "n_pairs": len(pairs),
        "mean_paired_difference": float(totals.sum() / sizes.sum()),
        "confidence": confidence, "ci_low": float(lo), "ci_high": float(hi),
        "bootstrap_resamples": n_resamples, "rng_seed": seed,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSON with records from a paired benchmark")
    parser.add_argument("--output", required=True)
    parser.add_argument("--n-resamples", type=int, default=10000)
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text())
    result = seed_clustered_paired_bootstrap(
        data["records"], "B4_ROBUST_JOINT", "B3_DETERMINISTIC_JOINT",
        n_resamples=args.n_resamples)
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
