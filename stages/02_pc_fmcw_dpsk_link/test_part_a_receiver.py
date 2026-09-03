import importlib.util
from pathlib import Path
import numpy as np

P=Path(__file__).with_name('part_a_receiver.py'); s=importlib.util.spec_from_file_location('rx',P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)

def test_noiseless_dbpsk_recovery():
    fs=16e9; ts=1e-9; n=16000; rng=np.random.default_rng(7); bits=rng.integers(0,2,999,dtype=np.int8)
    phase=np.mod(np.cumsum(np.pi*bits),2*np.pi); t=np.arange(n)/fs
    idx=np.clip(np.floor(t/ts).astype(int),0,len(bits)-1)
    # constant carrier is a valid limiting case for receiver decision testing
    tx=np.exp(1j*(2*np.pi*1e9*t+phase[idx]))
    hat,_=m.recover_dbpsk(tx,fs,ts)
    ref=np.real(np.exp(1j*phase[1:])*np.conj(np.exp(1j*phase[:-1])))<0
    k=min(len(hat),len(ref)); assert np.mean(hat[:k]!=ref[:k]) < 0.01

def test_observations_are_finite():
    fs=8e9; ts=2e-9; t=np.arange(8000)/fs; rx=np.exp(1j*2*np.pi*0.5e9*t)
    _,z=m.recover_dbpsk(rx,fs,ts); assert np.isfinite(z).all()
