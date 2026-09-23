# AWMA representative-suite refinement V2

Status: PROVISIONAL_SUITE_FREEZE_RECOMMENDATION

Authorities: Lane A structural catalog 2e8680dc4cc25e2409c2ef37a15ae8c2fc29ae9f and Lane C
asset audit 03924689da9c9691501d93567365c9265178b8a5. No capture, simulation,
mechanism run, Node109 action, or Lane B mutation occurred.

The prior exact-safe Lane A catalog closes V2/Lane-C identity using phase,
family, narrowly normalized implementation match key, grid, and block. Asset
status is therefore taken only from that closed catalog, not V1 surface text.
REUSABLE_NOW and REQUIRES_REQUALIFICATION selections are not new-capture demand.

Decode trajectory definition: same family, exact implementation, block, and
implementation semantics; all source-observed per-step grid/duration/recurrence
remain in DECODE_SHAPE_TRAJECTORIES.tsv. A monotonic grid evolution is one
DECODE_SHAPE_TRAJECTORY and is represented at steps 1/16/32; switch, nonmonotonic,
or material duration-regime changes must split trajectories in a later rerun.

Recommended minimal suite is 22 targets. It covers 79,254,495 ns / 154,876,910 ns
full S2 (51.17%), 82.47% of Prefill full-workload time, and 43.02% Decode
full-workload time. It has 3 REUSABLE_NOW, 1 REQUIRES_REQUALIFICATION, and 18
MISSING_SIM_TRACE rows. These missing rows are a V2-weighted review list, not
capture authorization.

STATISTICAL_HOLDOUT is the prior deterministic 20% launch-record split and is
only stability/weight validation. SCIENTIFIC_HOLDOUT_REQUIREMENT is separate:
reserve at least one unselected kernel/shape trajectory, never sharing a target
identity with mechanism discovery, plus future cross-context and distinct
model-family samples. T0/T1/T2 and random records from a selected stratum do
not qualify as scientific holdouts.
