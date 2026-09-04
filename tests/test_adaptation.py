from pcfmcw_isac.adaptation import PhyAction, QoSTarget, PredictedOutcome, select_nominal, select_chance_constrained


def test_nominal_selects_lowest_cost_feasible_action():
    acts = [PhyAction('a0', 1.0, 1), PhyAction('a1', 2.0, 2)]
    q = QoSTarget(ber_max=1e-2, rate_min_bps=1e5, range_rmse_max_m=2, velocity_rmse_max_mps=2)
    def pred(a):
        return PredictedOutcome(1e-1 if a.name=='a0' else 1e-3, 2e5, 1, 1)
    assert select_nominal(acts, pred, q).name == 'a1'


def test_chance_constraint_respects_probability():
    acts = [PhyAction('cheap', 1.0, 1), PhyAction('safe', 2.0, 2)]
    q = QoSTarget(ber_max=1e-2, rate_min_bps=1e5, range_rmse_max_m=2, velocity_rmse_max_mps=2, reliability=.9)
    def sampler(a, n):
        good = PredictedOutcome(1e-3, 2e5, 1, 1)
        bad = PredictedOutcome(1e-1, 2e5, 1, 1)
        if a.name == 'cheap':
            return [good] * 80 + [bad] * 20
        return [good] * n
    assert select_chance_constrained(acts, sampler, q, 100).name == 'safe'
