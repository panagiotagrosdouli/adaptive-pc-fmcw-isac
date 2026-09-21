import numpy as np
import pytest
from pcfmcw_isac.models import QoS, State
from pcfmcw_isac.policies import default_codebook, select_configuration


def test_all_deployable_policies_return_codebook_configuration():
    s = State(10.0, 500.0)
    q = QoS()
    codebook = default_codebook()
    for name in ("B0_fixed", "B1_comm", "B2_sensing", "B3_joint", "B4_robust"):
        c = select_configuration(name, s, q, codebook, np.random.default_rng(1), 1.0)
        assert c in codebook


def test_oracle_requires_truth():
    with pytest.raises(ValueError):
        select_configuration("oracle", State(5, 0), QoS())


def test_unknown_policy_fails_closed():
    with pytest.raises(ValueError):
        select_configuration("not-a-policy", State(5, 0), QoS())
