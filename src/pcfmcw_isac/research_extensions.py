"""Post-freeze research experiments for calibration, action-space sensitivity and distribution shift.

All outputs are simulation/analytical evidence, never hardware measurements.
The frozen publication-v2.1 benchmark is not modified by this module.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, replace
from typing import Iterable

import numpy as np

from .part_b_completion import _full_metrics, _robust_success_table, _select_from_table
from .policy_evaluation import _estimated_state, normalized_resource_cost, profile_registry
from .policy_v2_1 import _action_seed, _predict_metrics_v2_1
from .publication_benchmark import benchmark_states
from .publication_protocol import FROZEN_PROTOCOL_V1, PhyActionSpec, filter_physics_feasible_actions
from .statistics import wilson_lower_bound
from .supplemental_evidence_v2_1 import (
    _deterministic_select_from_controller_state,
    _evaluate_selected,
    _robust_select_custom,
)


def _restricted_select(state, *, robust_draws:int, allowed_profiles:set[str]|None=None, allowed_chips:set[int]|None=None, allowed_repetitions:set[int]|None=None, allowed_backoff_db:set[float]|None=None)->PhyActionSpec|None:
    estimated=_estimated_state(state,state.state_uncertainty_scale); table=_robust_success_table(state,estimated,robust_draws=robust_draws); target=FROZEN_PROTOCOL_V1.qos.joint_reliability_target; accepted=[]
    for action,(lower,_) in table.items():
        if lower<target: continue
        if allowed_profiles is not None and action.profile_name not in allowed_profiles: continue
        if allowed_chips is not None and action.chips_per_chirp not in allowed_chips: continue
        if allowed_repetitions is not None and action.repetition_factor not in allowed_repetitions: continue
        if allowed_backoff_db is not None and action.tx_power_backoff_db not in allowed_backoff_db: continue
        accepted.append(action)
    if not accepted: return None
    return min(accepted,key=lambda a:(normalized_resource_cost(a),a.profile_name,a.chips_per_chirp,a.repetition_factor,a.tx_power_backoff_db))


def _cumulative_robust_tables(state, estimated, checkpoints:tuple[int,...])->dict[int,dict]:
    """Generate one uncertainty stream/action and snapshot Wilson tables at checkpoints.

    Because every checkpoint consumes a prefix of the exact same action-local RNG
    stream, this is statistically equivalent to rerunning the current deterministic
    sampler at each draw count while avoiding repeated prefix computation.
    """
    if not checkpoints or any(n<=0 for n in checkpoints): raise ValueError("checkpoints must be positive")
    checkpoints=tuple(sorted(set(int(n) for n in checkpoints))); checkpoint_set=set(checkpoints); max_draws=checkpoints[-1]
    actions=filter_physics_feasible_actions(FROZEN_PROTOCOL_V1.actions(),profile_registry(),estimated)
    tables={n:{} for n in checkpoints}; u=state.state_uncertainty_scale
    for action in actions:
        rng=np.random.default_rng(_action_seed(state,action)); success=0
        for i in range(1,max_draws+1):
            draw=replace(estimated,
                ebn0_db=estimated.ebn0_db+rng.normal(0.0,1.5*u),
                if_snr_db=estimated.if_snr_db+rng.normal(0.0,1.5*u),
                radial_velocity_mps=estimated.radial_velocity_mps+rng.normal(0.0,1.0*u),
                residual_cfo_hz=max(0.0,estimated.residual_cfo_hz+rng.normal(0.0,250.0*u)))
            feasible,c_ok,s_ok,_=_predict_metrics_v2_1(action,draw); success+=int(feasible and c_ok and s_ok)
            if i in checkpoint_set: tables[i][action]=(wilson_lower_bound(success,i,confidence=0.95),success)
    return tables


def run_reliability_calibration(*,seeds:Iterable[int],robust_draws_values:Iterable[int]=(32,64,128,256,512),reference_draws:int=4096,target:float=0.95)->dict:
    """Quantify finite-draw decision error against a lower-noise high-draw reference."""
    draws_values=tuple(sorted(set(int(x) for x in robust_draws_values)))
    if any(x<=0 for x in draws_values) or reference_draws<=0: raise ValueError("draw counts must be positive")
    if reference_draws<max(draws_values): raise ValueError("reference_draws must be >= all finite draw counts")
    if not 0.0<target<1.0: raise ValueError("target must be in (0,1)")
    checkpoints=tuple(sorted(set(draws_values+(reference_draws,)))); records=[]
    for seed in seeds:
        for scenario_id,state in enumerate(benchmark_states(int(seed))):
            estimated=_estimated_state(state,state.state_uncertainty_scale); tables=_cumulative_robust_tables(state,estimated,checkpoints)
            reference_action=_select_from_table(tables[reference_draws],target); reference_feasible=reference_action is not None
            for draws in draws_values:
                action=_select_from_table(tables[draws],target); feasible=action is not None
                records.append({"seed":int(seed),"scenario_id":scenario_id,"robust_draws":draws,"target":target,"reference_draws":reference_draws,
                    "reference_feasible":reference_feasible,"finite_feasible":feasible,"false_feasible":bool(feasible and not reference_feasible),
                    "false_infeasible":bool((not feasible) and reference_feasible),"same_selected_action":bool(action==reference_action),
                    "selected_action":asdict(action) if action is not None else None,"reference_action":asdict(reference_action) if reference_action is not None else None})
    summary={}
    for draws in draws_values:
        rows=[r for r in records if r["robust_draws"]==draws]; n=len(rows)
        summary[str(draws)]={"n":n,"false_feasible_rate":sum(r["false_feasible"] for r in rows)/n if n else None,
            "false_infeasible_rate":sum(r["false_infeasible"] for r in rows)/n if n else None,
            "decision_disagreement_rate":sum(r["finite_feasible"]!=r["reference_feasible"] for r in rows)/n if n else None,
            "selected_action_disagreement_rate":sum(not r["same_selected_action"] for r in rows)/n if n else None,
            "finite_selection_rate":sum(r["finite_feasible"] for r in rows)/n if n else None,
            "reference_selection_rate":sum(r["reference_feasible"] for r in rows)/n if n else None}
    return {"records":records,"summary":summary,"reference_note":"The high-draw reference reduces Monte Carlo decision noise but is not physical ground truth.",
            "sampling_note":"All draw-count decisions use nested prefixes of the same deterministic action-local uncertainty stream."}


def run_action_space_sensitivity(*,seeds:Iterable[int],comm_bits:int=5_000,sensing_trials:int=1,robust_draws:int=256)->dict:
    variants={"FULL":{},"HIGH_MOBILITY_PROFILE_ONLY":{"allowed_profiles":{"ti_77ghz_high_mobility_capability_profile"}},"PARKING_PROFILE_ONLY":{"allowed_profiles":{"ti_77ghz_parking_profile"}},"NO_REPETITION":{"allowed_repetitions":{1}},"FIXED_32_CHIPS":{"allowed_chips":{32}},"NO_POWER_BACKOFF":{"allowed_backoff_db":{0.0}}}; records=[]
    for seed in seeds:
        for scenario_id,state in enumerate(benchmark_states(int(seed))):
            for label,restrictions in variants.items():
                action=_restricted_select(state,robust_draws=robust_draws,**restrictions); out=_evaluate_selected(label,action,state,comm_bits=comm_bits,sensing_trials=sensing_trials)
                records.append({"variant":label,"seed":int(seed),"scenario_id":scenario_id,"state":asdict(state),**out})
    summary={label:_full_metrics([r for r in records if r["variant"]==label]) for label in variants}; action_frequency={}
    for label in variants:
        rows=[r for r in records if r["variant"]==label and r.get("selected_action") is not None]
        counts=Counter((r["selected_action"]["profile_name"],r["selected_action"]["chips_per_chirp"],r["selected_action"]["tx_power_backoff_db"],r["selected_action"]["repetition_factor"]) for r in rows)
        action_frequency[label]={str(k):int(v) for k,v in counts.most_common()}
    return {"records":records,"summary":summary,"action_frequency":action_frequency}


def _shifted_truth(controller_state,family:str,rng:np.random.Generator):
    u=max(float(controller_state.state_uncertainty_scale),1.0)
    if family=="NOMINAL_GAUSSIAN":
        de,di,dv,dc=rng.normal(0.0,[1.5*u,1.5*u,1.0*u,250.0*u]); return replace(controller_state,ebn0_db=controller_state.ebn0_db+de,if_snr_db=controller_state.if_snr_db+di,radial_velocity_mps=controller_state.radial_velocity_mps+dv,residual_cfo_hz=max(0.0,controller_state.residual_cfo_hz+dc))
    if family=="HEAVY_TAILED_T3":
        scale=np.sqrt(1.0/3.0); z=rng.standard_t(df=3,size=4)*scale; return replace(controller_state,ebn0_db=controller_state.ebn0_db+z[0]*1.5*u,if_snr_db=controller_state.if_snr_db+z[1]*1.5*u,radial_velocity_mps=controller_state.radial_velocity_mps+z[2]*u,residual_cfo_hz=max(0.0,controller_state.residual_cfo_hz+z[3]*250.0*u))
    if family=="CORRELATED_SNR_INTERFERENCE":
        latent=rng.normal(); eb=controller_state.ebn0_db-1.5*u*latent; if_snr=controller_state.if_snr_db-1.5*u*latent+rng.normal(0.0,0.4*u); base_inr=-10.0 if controller_state.inr_db is None else float(controller_state.inr_db); return replace(controller_state,ebn0_db=eb,if_snr_db=if_snr,inr_db=base_inr+3.0*u*latent)
    if family=="BIASED_STATE_ESTIMATE": return replace(controller_state,ebn0_db=controller_state.ebn0_db-2.0*u,if_snr_db=controller_state.if_snr_db-2.0*u,radial_velocity_mps=controller_state.radial_velocity_mps+2.0*u,residual_cfo_hz=controller_state.residual_cfo_hz+500.0*u)
    raise ValueError(f"unknown distribution-shift family {family!r}")


def run_distribution_shift(*,seeds:Iterable[int],comm_bits:int=5_000,sensing_trials:int=1,robust_draws:int=256,truth_draws_per_state:int=4)->dict:
    """Paired B3/B4 evaluation under heavy-tailed, correlated and biased truth."""
    if truth_draws_per_state<=0: raise ValueError("truth_draws_per_state must be positive")
    families=("NOMINAL_GAUSSIAN","HEAVY_TAILED_T3","CORRELATED_SNR_INTERFERENCE","BIASED_STATE_ESTIMATE"); records=[]
    for seed in seeds:
        for scenario_id,base in enumerate(benchmark_states(int(seed))):
            controller_state=_estimated_state(base,base.state_uncertainty_scale); b3=_deterministic_select_from_controller_state(controller_state); b4=_robust_select_custom(base,controller_state,robust_draws=robust_draws,use_physics_gate=True,require_joint_constraint=True)
            for family_index,family in enumerate(families):
                for draw in range(truth_draws_per_state):
                    rng=np.random.default_rng(int(seed)*100_003+scenario_id*1009+family_index*97+draw); true_state=_shifted_truth(controller_state,family,rng)
                    for policy,action in (("B3_DETERMINISTIC_JOINT",b3),("B4_ROBUST_JOINT",b4)):
                        out=_evaluate_selected(policy,action,true_state,comm_bits=comm_bits,sensing_trials=sensing_trials)
                        records.append({"family":family,"seed":int(seed),"scenario_id":scenario_id,"truth_draw":draw,"controller_state":asdict(controller_state),"true_state":asdict(true_state),**out})
    summary={family:{policy:_full_metrics([r for r in records if r["family"]==family and r["policy"]==policy]) for policy in ("B3_DETERMINISTIC_JOINT","B4_ROBUST_JOINT")} for family in families}
    return {"records":records,"summary":summary,"claim_boundary":"Controlled distribution-shift simulation only; not evidence of universal or real-world robustness."}
