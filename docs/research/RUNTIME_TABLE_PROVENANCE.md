# Supplemental Runtime Table Provenance

## Current status

The values below are **historical/pre-correction runtime evidence** from GitHub Actions supplemental run `34696063382`. They remain valid measurements of that exact code/evidence instance, but they are no longer designated as the final runtime table for the corrected source model.

Historical artifact: `supplemental-v2-1-runtime-37958fdca328e4434ca670cf667e33719edced44-34696063382` (artifact id `10300013349`).

Historical source commit: `37958fdca328e4434ca670cf667e33719edced44`.

| Robust draws | B3 median [ms] | B4 median [ms] |
|---:|---:|---:|
| 64 | 0.576 | 36.292 |
| 128 | 0.565 | 70.470 |
| 256 | 0.572 | 138.886 |
| 512 | 0.576 | 272.810 |

At 256 draws, the same historical artifact reports B4 p95 `279.712 ms` and mean `168.958 ms`. These are host-runtime measurements on GitHub Actions infrastructure, not embedded-target or hard-real-time measurements.

## Why revalidation is required

A later source audit corrected the Texas Instruments short-range profile to use the independently source-reported 40 MHz/us programmed chirp slope rather than inferring slope from 858 MHz valid sweep bandwidth and a 25.6 us ADC capture interval. Since the physical gate is part of the policy evaluation path, the reviewer-grade supplemental suite is being rerun as a distinct evidence instance.

The final manuscript runtime table must use the runtime artifact from the corrected supplemental run, even if its numerical values happen to be close to the historical values. No historical runtime value should be silently copied forward without matching run/commit provenance.
