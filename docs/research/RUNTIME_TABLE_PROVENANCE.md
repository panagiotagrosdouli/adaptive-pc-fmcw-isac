# Supplemental Runtime Table Provenance

The runtime table in `paper/supplemental_v2_1_tables.tex` is sourced from completed GitHub Actions supplemental run `34696063382`, artifact `supplemental-v2-1-runtime-37958fdca328e4434ca670cf667e33719edced44-34696063382` (artifact id `10300013349`).

Source commit: `37958fdca328e4434ca670cf667e33719edced44`.

The table reports policy medians from `runtime.json`:

| Robust draws | B3 median [ms] | B4 median [ms] |
|---:|---:|---:|
| 64 | 0.576 | 36.292 |
| 128 | 0.565 | 70.470 |
| 256 | 0.572 | 138.886 |
| 512 | 0.576 | 272.810 |

At 256 draws, the same artifact reports B4 p95 `279.712 ms` and mean `168.958 ms`. These are host-runtime measurements on GitHub Actions infrastructure, not embedded-target or hard-real-time measurements.

This provenance note exists to prevent reintroduction of values from the earlier supplemental runtime run into the final manuscript tables.
