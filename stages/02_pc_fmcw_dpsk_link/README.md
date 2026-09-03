# Stage 02 — PC-FMCW / DPSK Link Model

This stage turns future relative WOMD geometry into communication state for prediction and scheduling.

## Source boundary

The uploaded Part-A notebook fixes the PC-FMCW/DPSK communication waveform and receiver: 193.4 THz carrier, 10 GHz chirp bandwidth, 10 us chirp duration, 1 Gbit/s DBPSK timing, local per-symbol FFT carrier extraction, parabolic FFT-peak refinement, carrier phase-step compensation, and differential bit decisions. Its BER demonstration is an AWGN receiver test.

Part A does **not** provide a complete vehicular optical link budget. Therefore the geometry-dependent range/pointing/atmospheric mapping in this stage is explicitly a model-based extension for the new paper. It must never be described as WOMD-measured communication or as a Part-A-reported link budget.

## Canonical chain

```text
real WOMD relative geometry
  -> range + bearing
  -> frozen model-based SNR mapping
  -> receiver-derived Part-A BER LUT
  -> packet error rate
  -> delivered goodput
  -> outage
  -> usable-link lifetime
```

For packet length L and bit error probability p_b, the baseline independent-bit packet model is `PER = 1 - (1-p_b)^L`. Goodput is `R_b(1-PER)`. A link is unusable when it is outside the frozen FoV or when PER reaches the frozen outage threshold.

## Provenance rule

`link_model_config.json` separates `part_a_fixed` quantities from `paper_extension_assumptions`. The latter are sensitivity parameters, not empirical claims. They must be frozen before official held-out scheduling evaluation.

## Required execution

1. Generate the receiver-derived BER LUT with `build_ber_lut.py` using the frozen seed and bit budget.
2. Record the LUT SHA-256 manifest.
3. Run link-model invariant tests.
4. Run sensitivity sweeps for packet size, range exponent, atmospheric loss, pointing width/FoV and outage threshold.
5. Freeze the selected configuration before Stage 05/06 official held-out evaluation.

Stage 02 remains PARTIAL until the canonical LUT and sensitivity artifacts are actually generated and archived.
