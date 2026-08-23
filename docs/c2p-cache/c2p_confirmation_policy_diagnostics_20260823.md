# C2P+ confirmation-policy compact diagnosis (2026-08-23)

This is a compact diagnostic campaign, not a replacement for the matched
PC-hash versus AddrTopo matrix.  Its normal policy uses the same `64 x 4`
three-bit confirmation table, threshold `4`, exploration period `64`, and
four-probe hard cap as the qualified matrix.

## Scope and audit

The three diagnosis workloads are Rodinia Btree, ISPASS BFS, and ISPASS LPS.
For each, the observational run includes exhaustive control, PC-hash, and
capacity-matched AddrTopo.  All nine runs have the same backend revision,
simulator binary hash, CUDA runtime hash, and trace hash per workload.  The
observation report passed remote-hit/L2-avoidance, probe partition,
continuation/package partition, exact-tail, and stop-delay conservation.

Raw, reproducible outputs are kept outside Git at:

`/workspace/worktrees/accel-sim-c2p-addr-observe/hw_run/c2p-confirmation-diagnostics-v1-20260823/`

* `diagnostics_observe.md` contains the three read-only distributions.
* `diagnostics_experiment.md` contains the controlled policy variants.

## Read-only findings

The PC and AddrTopo observations record candidate-count-bin by probe ordinal
hit/miss distributions, the first exact peer remaining after each learned
stop, and delay from learned stop to lower send.

Across this compact set, every learned stop entered the lower path immediately:
all PC (`333,988`) and AddrTopo (`483,340`) samples were in the zero-existing-
fallback bucket and had zero stop-to-lower-send cycles.  Thus these three
counterexamples are not primarily explained by a queued fallback port.  The
dominant remaining loss is an early stop that leaves a later exact peer:
candidate bins with longer lists retain substantial next-peer-at-distance
one-to-four opportunity, especially AddrTopo bin 3.

## Controlled PC-hash variants

Both variants preserve the same table capacity and four-probe hard cap:

1. **smallfull:** after the mandatory first probe fails, candidate lists of
   at most four are scanned to completion.
2. **initial6/initial7:** only the table reset score changes from the normal
   `4` to `6` or `7`; hashing, capacity, threshold, and exploration are fixed.

| workload | smallfull cycles | smallfull L2 | smallfull remote hits | interpretation |
|---|---:|---:|---:|---|
| Btree | -0.66% | -2.68% | +21,586 | More short-list confirmation is beneficial. |
| BFS | +0.05% | +0.21% | -2,439 | Extra probes do not recover useful peers. |
| LPS | -0.43% | -3.80% | +13,388 | Strong short-list confirmation opportunity. |

`initial6` and `initial7` do change sampled table-score histograms, proving
that their config option is active, but do not give a stable cross-workload
benefit.  LPS converges to exactly the normal PC behavior; BFS trades small
cycle changes against worse L2/remote-hit metrics.  They are therefore not a
candidate default policy.

## Consequence for the main matrix

The qualified 16 canonical plus 8 V100-extension matrix remains deliberately
unchanged: control, PC-hash, and AddrTopo all use reset score `4` and have the
small-list rule disabled.  `smallfull` is an optimization hypothesis to study
separately, first on Btree/LPS-like candidate distributions; it must not be
used to claim a PC-versus-AddrTopo comparison without a matched AddrTopo
counterpart.

## Reproduction

```bash
export C2P_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-c2p-addr-observe
scripts/run_c2p_confirmation_diagnostics.sh --out-root "$OUT" --phase observe --jobs 3
scripts/run_c2p_confirmation_diagnostics.sh --out-root "$OUT" --phase experiment --jobs 3
python3 scripts/analyze_c2p_confirmation_diagnostics.py \
  --root "$OUT" --csv "$OUT/diagnostics_experiment.csv" \
  --markdown "$OUT/diagnostics_experiment.md" --require-experiments
```
