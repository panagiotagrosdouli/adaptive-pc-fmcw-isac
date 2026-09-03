"""Canonical Stage-04 objective composition.

Link/outage surrogates are injected by the training pipeline so this module does
not silently replace the frozen Stage-02 physical/link mapping.
"""
from __future__ import annotations
from dataclasses import dataclass
import torch

OBJECTIVES=("trajectory","trajectory_plus_link","trajectory_plus_outage","full_communication_aware")

@dataclass(frozen=True)
class LossWeights:
    lambda_link: float=0.0
    lambda_outage: float=0.0

def compose_loss(name,pred_xy,true_xy,*,weights=LossWeights(),link_loss=None,outage_loss=None):
    if name not in OBJECTIVES: raise ValueError(f"unknown objective: {name}")
    traj=torch.mean((pred_xy-true_xy)**2)
    total=traj; parts={"trajectory":traj}
    need_link=name in {"trajectory_plus_link","full_communication_aware"}
    need_out=name in {"trajectory_plus_outage","full_communication_aware"}
    if need_link:
        if link_loss is None: raise ValueError("selected objective requires frozen-link surrogate loss")
        total=total+weights.lambda_link*link_loss; parts["link"]=link_loss
    if need_out:
        if outage_loss is None: raise ValueError("selected objective requires outage surrogate loss")
        total=total+weights.lambda_outage*outage_loss; parts["outage"]=outage_loss
    parts["total"]=total; return total,parts
