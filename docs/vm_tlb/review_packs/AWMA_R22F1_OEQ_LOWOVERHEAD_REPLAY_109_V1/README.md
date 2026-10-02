# AWMA R22F1 OEQ exact-input low-overhead replay

Status `R22F1_FAMILY_GAP_UNRESOLVED`. Fixed OAM-S:0.1, real `sitraj.xyz` frame55, accepted sorted graph/permutation, pinned OEQ/NequIP, float32 and TF32 OFF. One non-timed complete energy+force call captured both true OEQ TP callsites and their force VJP upstream gradients; all tensors and outputs are hashed.

Same-input Aorder/Dready standalone output and force-required gradients qualified. Backward mode was frozen as 32-state bundle before timing. Formal forward and backward each used 10 warmups/arm/callsite and 5 groups ×8 one-event-pair 32-replay bundles/arm/callsite. All 320 formal outputs/gradients passed numerical checks. The combined family sign remained mixed. No new NSYS/NCU/NVBit/SASS, Donline, old holdout, Accel-Sim or node174 compute.

`TP_CALL_RECORDS.tsv`, `REPLAY_IMPLEMENTATION_IDENTITY.tsv`, `REPLAY_CORRECTNESS.tsv`, `FORWARD_TIMING.tsv`, `BACKWARD_TIMING.tsv` and `REPLAY_DECISION.json` give compact evidence. Large exact tensors, every formal output and timing status are indexed on node164.
