#!/usr/bin/env python3
"""Monte-Carlo BER-vs-SNR LUT using the preserved Part-A receiver."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np
from part_a_receiver import recover_dbpsk

FC_HZ=193.4e12; B_HZ=10e9; T_CHIRP_S=10e-6; DATA_RATE_BPS=1e9


def simulate(snr_db: float, bits: int, seed: int) -> tuple[int,int]:
    rng=np.random.default_rng(seed)
    # Keep the Part-A waveform sampling ratio: 131072 samples / 10 us.
    fs=131072/T_CHIRP_S; ts=1/DATA_RATE_BPS
    symbols=min(bits+1, int(T_CHIRP_S/ts))
    tx_bits=rng.integers(0,2,size=symbols,dtype=np.int8)
    phase=np.mod(np.cumsum(np.pi*tx_bits),2*np.pi)
    t=np.arange(131072)/fs
    idx=np.clip(np.searchsorted(np.arange(symbols+1)*ts,t,side='right')-1,0,symbols-1)
    chirp_phase=np.pi*(B_HZ/T_CHIRP_S)*t*t
    tx=np.exp(1j*(chirp_phase+phase[idx]))
    p=np.mean(np.abs(tx)**2); noise_p=p/(10**(snr_db/10))
    noise=np.sqrt(noise_p/2)*(rng.standard_normal(tx.shape)+1j*rng.standard_normal(tx.shape))
    hat,_=recover_dbpsk(tx+noise,fs,ts)
    ref=np.real(np.exp(1j*phase[1:])*np.conj(np.exp(1j*phase[:-1])))<0
    n=min(len(hat),len(ref),bits)
    return int(np.count_nonzero(hat[:n]!=ref[:n])),n


def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--seed',type=int,default=20260827); p.add_argument('--bits',type=int,default=250000)
    p.add_argument('--snr-min',type=float,default=-25); p.add_argument('--snr-max',type=float,default=5); p.add_argument('--snr-step',type=float,default=1)
    a=p.parse_args(); rows=[]
    for i,snr in enumerate(np.arange(a.snr_min,a.snr_max+0.5*a.snr_step,a.snr_step)):
        remaining=a.bits; errors=total=0; batch=0
        while remaining>0:
            n=min(remaining,9998); e,k=simulate(float(snr),n,a.seed+i*100003+batch); errors+=e; total+=k; remaining-=k; batch+=1
        rows.append((float(snr),errors/total,errors,total))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['snr_db','ber','bit_errors','bits']); w.writerows(rows)
    digest=hashlib.sha256(a.output.read_bytes()).hexdigest()
    manifest={'source':'Part-A notebook DPSK receiver branch','receiver':'FFT carrier extraction + differential DBPSK','fc_hz':FC_HZ,'bandwidth_hz':B_HZ,'chirp_s':T_CHIRP_S,'data_rate_bps':DATA_RATE_BPS,'seed':a.seed,'bits_per_snr':a.bits,'snr_db':[a.snr_min,a.snr_max,a.snr_step],'lut_sha256':digest,'scientific_scope':'Monte-Carlo AWGN receiver calibration; not a WOMD measurement'}
    a.manifest.parent.mkdir(parents=True,exist_ok=True); a.manifest.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps(manifest,indent=2,sort_keys=True))
if __name__=='__main__': main()
