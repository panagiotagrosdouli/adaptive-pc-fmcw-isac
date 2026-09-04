from pcfmcw_isac.profiles import default_operating_profiles
from pcfmcw_isac.profile_selection import PhysicalRequirement, physically_feasible, select_min_cost_physical_profile


def test_parking_profile_rejects_published_high_mobility_scale():
    profiles = default_operating_profiles()
    sr = next(p for p in profiles if p.name == "P-SR-C32")
    req = PhysicalRequirement(range_m=20.28, radial_velocity_mps=19.8563835818, min_raw_rate_bps=200_000)
    assert not physically_feasible(sr, req)


def test_high_mobility_profile_accepts_published_high_mobility_scale():
    profiles = default_operating_profiles()
    hm = next(p for p in profiles if p.name == "P-HM-C32")
    req = PhysicalRequirement(range_m=20.28, radial_velocity_mps=19.8563835818, min_raw_rate_bps=200_000)
    assert physically_feasible(hm, req)


def test_min_cost_selector_uses_short_range_profile_when_physics_allow_it():
    profiles = default_operating_profiles()
    req = PhysicalRequirement(range_m=10.0, radial_velocity_mps=3.0, min_raw_rate_bps=200_000)
    selected = select_min_cost_physical_profile(profiles, req)
    assert selected is not None
    assert selected.name == "P-SR-C32"


def test_min_cost_selector_escalates_to_high_mobility_profile():
    profiles = default_operating_profiles()
    req = PhysicalRequirement(range_m=20.28, radial_velocity_mps=19.8563835818, min_raw_rate_bps=200_000)
    selected = select_min_cost_physical_profile(profiles, req)
    assert selected is not None
    assert selected.name == "P-HM-C16"
