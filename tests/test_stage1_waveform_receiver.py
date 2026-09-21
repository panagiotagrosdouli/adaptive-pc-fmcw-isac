import numpy as np
from pcfmcw_isac.waveform import WaveformConfig, differential_bpsk_phases, generate_pc_fmcw
from pcfmcw_isac.receivers import decode_dbpsk, dechirp, range_doppler_map
from pcfmcw_isac.channel import add_awgn


def test_dbpsk_noiseless_roundtrip():
    cfg = WaveformConfig(n_chirps=16)
    bits = np.array([0,1,1,0,1,0,0,1,1,1,0,0,1,0,1])
    phases = differential_bpsk_phases(bits)
    _, tx = generate_pc_fmcw(cfg, phases)
    _, ref = generate_pc_fmcw(cfg, np.zeros(cfg.n_chirps))
    dec = decode_dbpsk(tx, ref)
    assert np.array_equal(dec, bits)


def test_awgn_high_snr_dbpsk():
    cfg = WaveformConfig(n_chirps=64)
    rng = np.random.default_rng(4)
    bits = rng.integers(0, 2, cfg.n_chirps - 1)
    phases = differential_bpsk_phases(bits)
    _, tx = generate_pc_fmcw(cfg, phases)
    _, ref = generate_pc_fmcw(cfg, np.zeros(cfg.n_chirps))
    rx = add_awgn(tx, 30.0, rng)
    dec = decode_dbpsk(rx, ref)
    assert np.mean(dec != bits) < 0.02


def test_dechirp_shape_and_rd_map():
    cfg = WaveformConfig(n_chirps=8)
    _, tx = generate_pc_fmcw(cfg, np.zeros(cfg.n_chirps))
    beat = dechirp(tx, tx)
    assert beat.shape == tx.shape
    rd = range_doppler_map(tx, tx)
    assert rd.shape == tx.shape
