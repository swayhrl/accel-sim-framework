# Stage C candidate freeze — before formal Q1 timing

Scientific index remains the accepted V1 IVF-PQ graph SHA256 `a68d4a2905fcab13a40872db73165fb4271a493f09b9fd61f5f1e9a401f073b8` and serialized SHA256 `6cddddb35f63d31b1308d1411d76aabcef910b11caea1778ca823f4fb63e7151`. No second index was built. Discovery IDs 0..255 only; sealed 256..511 unopened; k=10 and recall gate 0.95 unchanged.

The first four high-itopk A1 points were all measured, and two passed:

| Frozen formal candidate | Mode | itopk | width | Source-derived CTAs/query | Discovery recall@10 |
|---|---|---:|---:|---:|---:|
| `Q1_SINGLE_512_1` | SINGLE_CTA | 512 | 1 | 1 | 0.959765625 |
| `Q1_MULTI_512_1` | MULTI_CTA | 512 | 1 | 16 | 0.961328125 |

All previously measured lower-itopk points failed 0.95; `SINGLE_CTA 128/1=0.880859375`, `256/1=0.928906250`. The accepted Q1 AUTO/default 64/1 had recall 0.791015625. AUTO with itopk512/1 would source-resolve to MULTI_CTA on 76-SM RTX4080 and is not an independent third candidate. A2 widths and the NN-DESCENT second-index branch are therefore **not triggered**. Candidates were chosen by lowest qualified itopk then width, not preliminary timing.

Formal acquisition is frozen to 3 paired groups. Arm order: group0 SINGLE→MULTI, group1 MULTI→SINGLE, group2 SINGLE→MULTI. Each arm/group receives 2 complete 256-query warmup repeats followed by 5 formal repeats. Each repeat makes 256 separate Q1 searches over the exact discovery query order. Query and output arrays are GPU-resident/preallocated; host wall ends after GPU completion. All per-query values go to node164 raw, compact per-repeat values to Git. Fastest quality-reproducing formal candidate becomes `Q1_STRONG_V2`; no holdout or parameter changes may influence selection.
