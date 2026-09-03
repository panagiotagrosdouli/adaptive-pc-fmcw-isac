"""Common scheduler contract for paired vehicular communication experiments."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class SchedulerState:
    queue_bits: np.ndarray
    current_goodput_bps: np.ndarray
    avg_served_bps: np.ndarray
    predicted_goodput_bps: np.ndarray | None = None  # [vehicles,horizon]
    predicted_outage: np.ndarray | None = None       # [vehicles,horizon]

class RandomScheduler:
    name="Random"
    def __init__(self,seed=0): self.rng=np.random.default_rng(seed)
    def select(self,s:SchedulerState):
        eligible=np.flatnonzero(s.queue_bits>0); return None if not len(eligible) else int(self.rng.choice(eligible))

class RoundRobin:
    name="Round-Robin"
    def __init__(self): self.cursor=0
    def select(self,s):
        n=len(s.queue_bits)
        for k in range(n):
            i=(self.cursor+k)%n
            if s.queue_bits[i]>0: self.cursor=(i+1)%n; return i
        return None

class ReactiveGreedy:
    name="Reactive-Greedy"
    def select(self,s):
        score=np.where(s.queue_bits>0,s.current_goodput_bps,-np.inf); i=int(np.argmax(score)); return None if not np.isfinite(score[i]) else i

class ProportionalFair:
    name="PF"
    def __init__(self,epsilon=1.0): self.epsilon=epsilon
    def select(self,s):
        score=np.where(s.queue_bits>0,s.current_goodput_bps/np.maximum(s.avg_served_bps,self.epsilon),-np.inf); i=int(np.argmax(score)); return None if not np.isfinite(score[i]) else i

class PredictiveUtility:
    name="Predictive-Utility"
    def __init__(self,horizon_steps=10,outage_penalty=1.0): self.h=horizon_steps; self.penalty=outage_penalty
    def select(self,s):
        if s.predicted_goodput_bps is None: raise ValueError("predictive scheduler requires predicted_goodput_bps")
        g=s.predicted_goodput_bps[:,:self.h]; utility=np.mean(g,axis=1)
        if s.predicted_outage is not None: utility-=self.penalty*np.mean(s.predicted_outage[:,:self.h],axis=1)*np.maximum(np.max(g),1.0)
        score=np.where(s.queue_bits>0,utility,-np.inf); i=int(np.argmax(score)); return None if not np.isfinite(score[i]) else i

class LinkLifetimeScheduler:
    name="Link-Lifetime"
    def __init__(self,horizon_steps=20): self.h=horizon_steps
    def select(self,s):
        if s.predicted_outage is None: raise ValueError("link-lifetime scheduler requires predicted_outage")
        o=s.predicted_outage[:,:self.h].astype(bool); life=np.array([np.flatnonzero(x)[0] if np.any(x) else self.h for x in o],float)
        # Serve links predicted to disappear soon, while requiring queued traffic.
        score=np.where(s.queue_bits>0,-life,-np.inf); i=int(np.argmax(score)); return None if not np.isfinite(score[i]) else i
