# Lane 6 — paper prose, evidence map, figures and PPA r1

Status: documentation/artifact candidate, independent review required.
Coordination: `6c136e2a56a008695f8c8b815723bf8f1a760db9`.
Scope: Framework documentation and offline tools only. No mechanism, runner,
benchmark, configuration, raw log or upstream scientific CSV was modified.

Start with `PAPER_DRAFT_ZH_V1.md`: it contains written introduction, problem,
architecture, lifecycle/interface, methodology and PPA sections. This is not
an outline. `CLAIM_EVIDENCE_MAP.md` distinguishes historical implementation,
historical measurements, shadow evidence, oracle-assisted designs, ideal
diagnostics and missing new functional results. `PPA_LEDGER.md` is a concrete
raw-bit/operation ledger with unknown physical terms left explicit.

## Outputs

- `PAPER_DRAFT_ZH_V1.md`, `CLAIM_EVIDENCE_MAP.md`, `PPA_LEDGER.md`.
- `REMAINING_EVIDENCE.md`: owner-specific gates to complete paper claims.
- `FIGURE_INPUT_MANIFEST.json`, `SOURCE_EVIDENCE_MANIFEST.json`,
  `DEPENDENCY_SNAPSHOT.json`: full revisions, exact source blob hashes and
  bounded Lane-1/4/5 publication snapshot.
- `PPA_BITS.json`, `DATA_BUDGET.csv`, `PPA_STORAGE_SCENARIOS.csv`: generated
  Lane-6 accounting outputs, not modified experiment CSVs.
- `figures/FIG01_LIFECYCLE_ARCHITECTURE.mmd`: editable design-contract figure.
- Four PDF/SVG figures: data budget, historical D512 sensitivity, historical
  MSHR sensitivity, and archived sector-reuse observation. All captions state
  evidence type. No new implementation or ideal performance bar exists.
- `RESULT_INPUT_CONTRACT.md`, `plot_verified_results.py`: future hash-bound
  Lane-4/5 result intake. Only first-WB functional comparisons and separately
  labelled ideal comparisons are currently enabled. Oracle/TVD additions need
  their own reviewed transition contract; unsupported combinations fail closed.
- `VALIDATION.md`, `validation/`, `SHA256SUMS`: commands/results and artifact
  integrity. Test fixtures are synthetic intake tests, never simulator results.

## Reproduce without changing scientific inputs

Use the committed generator source revision recorded in the manifest. A clean
temporary worktree at that revision avoids confusing publication and producer
identities. Source objects from the exact Framework/Core revisions in the
source manifest must be available locally. Python requirements: Python 3 and
Matplotlib (observed `/usr/bin/python3`, Matplotlib 3.10.9). Git is required.
The scripts do not fetch, run a simulator or modify any input record.

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \
  docs/ep_l2/review_packs/FT20261016_LANE6_PAPER_PPA_r1/build_figures.py \
  --framework-repo /path/to/producer-worktree \
  --core-repo /path/to/readonly-core-repository \
  --output-dir /tmp/lane6-reproduction

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \
  docs/ep_l2/review_packs/FT20261016_LANE6_PAPER_PPA_r1/test_result_intake.py
```

Rendering is deterministic within the recorded toolchain. Run against a new
output directory for comparison; do not regenerate over this published pack.
The generator refuses uncommitted source changes. Scientific experiment data
is read with `git show` from exact commits and is not copied into a new
runtime-authority table.

## Current dependency interpretation

Lane-1 interface publication `cb7d92e4` is available and consumed, Core
interface source `4fb91f0a`; its baseline is not runtime-ready. Lane-4 and
Lane-5 receipts were read at `1657e770` and `cc97ee2a`; neither supplied a new
complete result manifest. These are fixed snapshots, not assertions about
later branch tips. Missing results leave only the affected claims pending;
paper prose and storage calculations are already produced.

The old 1152-slot model is not the new B16. Static and Unified C16 both use
1168×128B=146KiB/slice, 9.125MiB/chip; C8 uses 145KiB/slice,
9.0625MiB/chip. The ledger does not turn raw bit ratios into area/power.
Historical RTL exists, but matched B16/Unified changed RTL and process/clock
constraints have not been supplied. No unrelated historical synthesis is
represented as an EP-L2 differential result.
