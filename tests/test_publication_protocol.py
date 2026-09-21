from pcfmcw_isac.if_model import RadarProfile
from pcfmcw_isac.publication_protocol import (
    FROZEN_PROTOCOL_V1,
    EvaluationState,
    PhyActionSpec,
    action_physics_feasibility,
    filter_physics_feasible_actions,
    is_physics_feasible,
    physics_feasibility,
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
    assert len(FROZEN_PROTOCOL_V1.actions()) == 54


def test_final_seed_family_is_disjoint_from_pilot_style_small_seeds():
    seeds = list(FROZEN_PROTOCOL_V1.final_seeds())
    assert seeds[0] == 10_000
    assert seeds[-1] == 10_999
    assert len(seeds) == 1_000
    assert not set(range(10)).intersection(seeds)


def test_parking_profile_rejects_high_velocity_with_reason():
    parking = RadarProfile()
    state = make_state(range_m=10.0, velocity_mps=20.0)
    result = physics_feasibility(parking, state)
    assert parking.max_unambiguous_velocity_mps < 20.0
    assert not result.feasible
    assert result.reasons == ("VELOCITY_AMBIGUOUS",)
    assert not is_physics_feasible(parking, state)


def test_parking_profile_accepts_short_range_low_velocity():
    parking = RadarProfile()
    state = make_state(range_m=10.0, velocity_mps=3.0)
    result = physics_feasibility(parking, state)
    assert result.feasible
    assert result.reasons == ()


def test_physics_gate_reports_multiple_independent_failures():
    parking = RadarProfile()
    state = make_state(
        range_m=parking.positive_if_max_range_m + 1.0,
        velocity_mps=parking.max_unambiguous_velocity_mps + 1.0,
    )
    result = physics_feasibility(parking, state)
    assert not result.feasible
    assert set(result.reasons) == {"RANGE_UNSUPPORTED", "VELOCITY_AMBIGUOUS"}


def test_physics_gate_is_inclusive_at_exact_support_boundaries():
    parking = RadarProfile()
    state = make_state(
        range_m=parking.positive_if_max_range_m,
        velocity_mps=parking.max_unambiguous_velocity_mps,
    )
    assert physics_feasibility(parking, state).feasible


def test_action_gate_reports_missing_profile_without_exception():
    action = PhyActionSpec("missing_profile", 32, 0.0, 1)
    result = action_physics_feasibility(action, {}, make_state(10.0, 0.0))
    assert not result.feasible
    assert result.reasons == ("PROFILE_MISSING",)


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
    assert {a.profile_name for a in feasible} == {"ti_77ghz_high_mobility_capability_profile"}
