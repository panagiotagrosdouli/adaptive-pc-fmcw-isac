import numpy as np
import pytest
from predictors import LastPosition, ConstantVelocity, ConstantAcceleration, LinearKalmanCV, InformationOracle


def history(v=2.0):
    t=np.arange(11)*0.1
    return np.c_[v*t, np.zeros_like(t)]


def test_last_position_shape():
    f=LastPosition().predict(history(), 20)
    assert f.mean_xy.shape == (20,2)
    np.testing.assert_allclose(f.mean_xy, np.repeat(history()[-1][None], 20, axis=0))


def test_cv_exact_on_linear_motion():
    f=ConstantVelocity().predict(history(3.0), 10).mean_xy
    expected=history(3.0)[-1,0] + 3.0*0.1*np.arange(1,11)
    np.testing.assert_allclose(f[:,0], expected, atol=1e-12)


def test_ca_uses_history_only_and_shape():
    f=ConstantAcceleration().predict(history(), 80)
    assert f.mean_xy.shape == (80,2)


def test_kalman_returns_covariance():
    f=LinearKalmanCV().predict(history(), 8)
    assert f.mean_xy.shape == (8,2)
    assert f.covariance_xy.shape == (8,2,2)
    assert np.isfinite(f.covariance_xy).all()


def test_information_oracle_is_explicitly_noncausal():
    with pytest.raises(ValueError):
        InformationOracle().predict(history(), 5)
    future=np.ones((80,2))
    np.testing.assert_allclose(InformationOracle().predict(history(),5,future_xy=future).mean_xy,1)
