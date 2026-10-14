"""Post-freeze census invariants; historical publication numbers remain frozen."""
from pathlib import Path
from runpy import run_path

census = run_path(str(Path(__file__).resolve().parents[1] /
    "scripts" / "run_coupled_if_research.py"))["census"]

def test_coupled_census_matches_grid_size_and_historical_support():
    data = census("complex", 0.0)
    assert data["n"] == 238
    assert data["independent_supported"] == 132
    assert 0 <= data["coupled_supported"] <= 238
    assert data["evidence"] == "POST_FREEZE_ANALYTICAL_CENSUS_NOT_RECEIVER_VALIDATED"

def test_passband_conventions_report_explicitly():
    complex_data = census("complex", 0.0)
    positive_data = census("positive", 0.0)
    assert complex_data["convention"] == "complex"
    assert positive_data["convention"] == "positive"
    # No silent equivalence between positive-only and signed IF support.
    assert positive_data["coupled_supported"] <= complex_data["coupled_supported"]

def test_guard_does_not_expand_admissible_region():
    base = census("complex", 0.0)
    guarded = census("complex", 0.05)
    assert guarded["coupled_supported"] <= base["coupled_supported"]
