from pcfmcw_isac.if_model import RadarProfile
from pcfmcw_isac.publication_protocol import (
    FROZEN_PROTOCOL_V1,
    EvaluationState,
    filter_physics_feasible_actions,
    is_physics_feasible,
)


def make_state(range_m: float, velocity_mps: float) -> EvaluationState:
    return EvaluationState(
        ebn0_db=8.0,
        if_snr_db=10.0,
        range_m=range_m,
        radial_velocity_mps=velocity_mps,
        residual_cfo_hz=0.0,
        inr_db=None,
        phase_noise_std_rad_per_sample=0.0,
        state_uncertainty_scale=0.0,
        seed=10_000,
    )


def test_frozen_protocol_is_valid_and_has_expected_action_count():
    FROZEN_PROTOCOL_V1.validate()
    # 2 profiles x 3 chip budgets x 3 power levels x 3 repetition factors.
    assert len(FROZEN_PROTOCOL_V1.actions()) == 54


def test_final_seed_family_is_disjoint_from_pilot_style_small_seeds():
    seeds = list(FROZEN_PROTOCOL_V1.final_seeds())
    assert seeds[0] == 10_000
    assert seeds[-1] == 10_999
    assert len(seeds) == 1_000
    assert not set(range(10)).intersection(seeds)


def test_parking_profile_rejects_high_velocity():
    parking = RadarProfile()
    state = make_state(range_m=10.0, velocity_mps=20.0)
    assert parking.max_unambiguous_velocity_mps < 20.0
    assert not is_physics_feasible(parking, state)


def test_parking_profile_accepts_short_range_low_velocity():
    parking = RadarProfile()
    state = make_state(range_m=10.0, velocity_mps=3.0)
    assert is_physics_feasible(parking, state)


def test_physics_gate_filters_actions_by_profile_support():
    parking = RadarProfile()
    high_mobility = RadarProfile(
        carrier_hz=77e9,
        bandwidth_hz=1e9,
        chirp_duration_s=20e-6,
        chirp_repetition_s=20e-6,
        sample_rate_hz=37.5e6,
        samples_per_chirp=750,
        n_chirps=128,
    )
    profiles = {
        "ti_77ghz_parking_profile": parking,
        "ti_77ghz_high_mobility_capability_profile": high_mobility,
    }
    state = make_state(range_m=20.0, velocity_mps=20.0)
    feasible = filter_physics_feasible_actions(FROZEN_PROTOCOL_V1.actions(), profiles, state)
    assert feasible
    assert {a.profile_name for a in feasible} == {
        "ti_77ghz_high_mobility_capability_profile"
    }
