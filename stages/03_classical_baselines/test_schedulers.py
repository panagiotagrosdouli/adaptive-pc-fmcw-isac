import numpy as np
import pytest
from schedulers import SchedulerState,RandomScheduler,RoundRobin,ReactiveGreedy,ProportionalFair,PredictiveUtility,LinkLifetimeScheduler

def state():
 return SchedulerState(np.array([100.,100.,0.]),np.array([5.,10.,99.]),np.array([5.,20.,1.]),np.array([[10.,9.,8.],[5.,20.,20.],[99.,99.,99.]]),np.array([[0,0,1],[0,0,0],[0,0,0]],bool))

def test_reactive_greedy_ignores_empty_queue(): assert ReactiveGreedy().select(state())==1
def test_pf_uses_common_average_service_state(): assert ProportionalFair().select(state())==0
def test_round_robin_is_deterministic():
 r=RoundRobin(); s=state(); assert [r.select(s),r.select(s),r.select(s)]==[0,1,0]
def test_random_is_seed_reproducible():
 a=RandomScheduler(7); b=RandomScheduler(7); assert [a.select(state()) for _ in range(10)]==[b.select(state()) for _ in range(10)]
def test_predictive_requires_prediction():
 s=state(); bare=SchedulerState(s.queue_bits,s.current_goodput_bps,s.avg_served_bps)
 with pytest.raises(ValueError): PredictiveUtility().select(bare)
def test_link_lifetime_prioritizes_soon_to_disappear(): assert LinkLifetimeScheduler(3).select(state())==0
