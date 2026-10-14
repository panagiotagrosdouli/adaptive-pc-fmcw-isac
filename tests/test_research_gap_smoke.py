from scripts.run_research_gap_smoke import run

def test_reproducible_and_separate_synthetic_benchmark():
    a=run(seed=17,n_cal=200,n_test=200,n_cases=12)
    b=run(seed=17,n_cal=200,n_test=200,n_cases=12)
    assert a==b
    assert a["evidence"]=="SYNTHETIC_SMOKE_NOT_PC_FMCW"
    assert a["calibration"]["n"]==200
    assert a["held_out"]["n"]==200
    assert 0 <= a["sequential"]["mean_draws"] <= 512
