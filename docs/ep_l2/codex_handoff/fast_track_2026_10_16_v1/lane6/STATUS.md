# Lane 6 — paper, evidence map, figures and PPA

Status: `READY_FOR_REVIEW` — paper/tool/accounting deliverables complete; new
mechanism performance and physical PPA remain `DEPENDENCY_PENDING`.
Date: 2026-10-16 (Asia/Shanghai). Host: `huangrulin-174`.

- Worktree: `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane6-v1`.
- Framework execution branch: `hrl/ep-l2-ft20261016-lane6-v1`.
- Frozen paper/tool source: `a792de58ce436fca225ee689a291a1b5fa8c3211`.
- Core execution branch/source/binary: none; no simulator build/run or Core edit.
- Coordination commit: `6c136e2a56a008695f8c8b815723bf8f1a760db9`.

## Completed

Written Chinese paper (11,268 characters including Markdown), introduction,
problem, architecture/lifecycle/API, methods, historical observations, explicit
new-result cells, and PPA method. Fourteen claim-to-source/test/CSV mappings;
parameterized field/operation/queue ledger; exact C16 1168-slot / C8 1160-slot
data budgets; six illustrative generation-width scenarios with unknown
physical terms preserved. Four PDF/SVG figures plus editable Mermaid design
source, full source/figure manifests, pending-evidence register and fail-closed
result plotting intake. No new speedup number is asserted.

Validation: 9 result-intake tests pass (including synthetic published-bundle
roundtrip, slowdown preservation and tamper rejection); 14 generated artifacts
byte-identical on regeneration; independent budget checks; all four rendered
PDFs visually inspected. No simulation experiment, RTL synthesis or silicon
PPA measurement was performed. Historical source/test records were read, not
rerun. No mechanism/input/upstream scientific CSV was changed.

## Consumed exact publications

- Lane 1 Framework `cb7d92e4edde97e81520cfdd00762dfe81ee9b20`: V1 interface
  and baseline receipt; Core interface `4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617`.
  `runtime_ready=false`; binary/config null. Interface publication is not
  functional runtime qualification.
- Lane 4 Framework `1657e77020321e0095acb2e7922056b27d8edf50`: initial receipt,
  no complete new result manifest.
- Lane 5 Framework `cc97ee2ad9feb4ff57482cb7d826a53a3a4d07a0`: host-budget
  receipt, no complete new result manifest.

These are bounded consumption snapshots, not claims about subsequent branch
tips. Exact file/blob hashes are in DEPENDENCY_SNAPSHOT and SOURCE_EVIDENCE_MANIFEST.

## Dependencies / next executable stage

Read Lane-1 qualified source/binary/config release and Lane-5 complete matched
B16/U_WB16 result manifests; separately consume Lane-4 diagnostic manifests.
Use hash-bound adapters and publish a new review-pack revision. Oracle/TVD
comparisons need their exact transition contracts. Differential synthesis needs
matched baseline/candidate RTL, technology/macros and clock/IO constraints;
historical V3 RTL and installed tools alone do not supply them.

No active Lane-6 simulator runs; no background continuation is claimed.
Documentation/PPA-bit deliverables are ready for independent review now.

Review pack: `docs/ep_l2/review_packs/FT20261016_LANE6_PAPER_PPA_r1/`.
RECEIPT: sibling `RECEIPT.json`. Publication SHA is supplied by the remote
execution branch and final report, never self-referenced in this receipt.
