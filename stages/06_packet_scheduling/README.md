# Stage 06 — Packet Scheduling

`simulator.py` implements the packet-level experiment core. It uses FIFO queues,
packet deadlines, partial service across slots, exponential throughput history
for proportional fairness, and the shared Stage-03 scheduler interface.

Scientific invariants enforced by the implementation:

- one seeded arrival trace is reused by all policies in a paired comparison;
- all policies are scored against the same ground-truth goodput/outage trace;
- predicted goodput and outage affect decisions only;
- expired or incomplete packets do not contribute to timely goodput;
- outputs retain packet delivery, deadline, latency, outage, throughput and Jain
  fairness metrics.

Run `make stage06-test`. The final publication matrix remains `PARTIAL` until the
Stage-05 artifacts are available and all declared scenario, seed, horizon,
vehicle-count and offered-load combinations have been executed and archived.
