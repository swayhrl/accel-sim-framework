# Open issues and limits

- S1 guarantees data availability without implementing its storage source; it
  remains an oracle, not hardware.
- H1 4 MiB real-producer storage was not reached because S1 failed the 5% gate.
  The Stage-A producer ledger must not be presented as an H1 performance
  result.
- Existing queue occupancy is recorded in the simulator's queue-length units.
  It is not converted into a new configured queue depth or hardware size.
- The screen uses one accepted L512 CONTEXT2 derived from the R101 workload.
  It is not a holdout or generalization result.
- No FULL5 response, capacity-matched control, area, timing, energy or Native
  causality result exists in this stage.
- The inherited combined service-mode print label is semantically awkward.
  It is documented and disambiguated by the command receipt; changing the
  frozen S1 binary solely for naming was not justified.
- S1's low cycle response despite large traffic reduction does not identify a
  single remaining bottleneck. Return-full telemetry is a mediator observation,
  not an additive attribution.
