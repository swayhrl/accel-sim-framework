# Baseline control-plane repair

The stale pre-recovery summaries in `AWMA_NEW_SIM_BASELINE_174NEW_V1` were
reconciled from its accepted recovery addendum and qualification decision. No
C12 replay was rerun.

The repaired files now identify the accepted source pair, qualified binary,
recovered Prefill/Decode list hashes and counts, accepted log hashes, real
parser result, and bounded replay result. Old `BLOCKED_INPUT_OR_RUNTIME` and
precursor-source statements were removed where contradicted by later accepted
evidence.

The repair does not broaden the scientific result. It remains exactly:

`NEW_SIM_BASELINE_V1_QUALIFIED / HASH_BOUND_FIXED_WINDOW_10000`

Historical binary identity, full-ROI execution, numerical equivalence, and a
current-model simulator-native input remain outside that claim.
