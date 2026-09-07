# B9 acceptance matrix

Goal: `B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT`

B9 is PASS only when every mandatory row below is satisfied. This is a static/preflight stage; any simulator execution is an automatic scope violation.

| ID | Requirement | Mandatory evidence |
|---|---|---|
| B9-A | B8 and A checkpoint provenance bound | Exact B8 `3c5700cb...`, A checkpoint `73d25ebb...`, current B binary/trace/config hashes recorded |
| B9-B | No heavy execution | No simulator, worker, rebuild, trace generation, full-ROI scan, or E01-E10 run |
| B9-C | E01-E06 exact configs frozen | Per arm command, baseline, immutable trace/ROI, config delta, realization guard, output path |
| B9-D | Config drift guarded | `ARM_DELTA_WHITELIST.tsv` proves only intended options change |
| B9-E | Queue/stall observables included | Hit/miss plus MSHR-full/PWQ/walk/PWC/PTE/cycles/IPC and realized controls where available |
| B9-F | A evidence used correctly | A motivates observables/order only; no cross-context numeric pooling or B performance claim |
| B9-G | E07/E08 calibration exact | Representative job, peak-RSS capture, swap/iowait/MemAvailable and integrity checks frozen |
| B9-H | E09/E10 selector deterministic | 16+16 matched signature-stratified selection algorithm and fallback rules frozen |
| B9-I | Execution script safe | Defaults dry-run, explicit enable required, concurrency 1, no overwrite, per-job resource gate, stateful ROI not split |
| B9-J | Result contract machine readable | PASS/FAIL/INVALID_CONFIG/INCONCLUSIVE/RESOURCE_DEFERRED and provenance fields defined |
| B9-K | Existing evidence preserved | B1-B8 scratch/evidence never overwritten or reclassified |
| B9-L | Evidence labels retained | All B output remains `SPECULATIVE_DIAGNOSTIC`; missing is not zero |
| B9-M | Static validation passes | Shell/Python syntax checks, config parser checks and dry-run rendering pass without executing jobs |
| B9-N | Final decision unique | Exactly one of READY / CONFIG_MISMATCH / USER_DECISION selected |
| B9-O | Stop boundary honored | Commit/push then STOP; E01-E10 not started |

## Additional interpretation rules

1. A's terminal C3 result that decode generic/paper are much slower than ideal/disabled is external evidence, not a B result.
2. A's paper-vs-generic example shows miss count alone is not a sufficient decision metric; B future experiments must retain pressure/stall observables.
3. `PREFLIGHT_BLOCKED_CONFIGURATION_MISMATCH` is a valid result if the frozen B binary cannot realize an experiment. Do not patch Core in B9 to force a PASS.
4. No resource threshold may be weakened simply because B9 is preparing a future execution pack.
