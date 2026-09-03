# M5.E1 Extended-20 formalization

Status: **IN PROGRESS — NO EXTENDED SIMULATIONS AUTHORIZED**

This is an E1 provenance inventory, not a formal result.  The approved
portfolio is frozen by `M5_EXTENDED20_APPROVAL.md` and
`extended20/EXTENDED20_APPROVED.tsv`; it has not been selected or reordered
using DTC performance.  M5.E2 remains blocked until M5.2 freezes the common
Core/Framework/config/parser/metric anchor.

## Starting anchors

| field | value |
| --- | --- |
| active Core branch | `hrl/decoupled-l1-m5-v0` |
| active Framework branch | `hrl/decoupled-l1-exp-m5-v0` |
| approved selection evidence | `hrl/decoupled-l1-exp-m5-extended20-select-v0@d43b6eec93f68efa94057f34ffa699463b53e6a6` |
| portfolio roster | `extended20/EXTENDED20_APPROVED.tsv` |
| CUDA samples candidate source | `/tmp/dtc-l1-m5-cuda-samples-probe.oDOw3x@b7c5481c556c3fe98db060207ecaa41a4b9a9abc` |
| Parboil candidate source | `/tmp/dtc-l1-m5-parboil@4e0fc54866546efa44fe93af57c9cef62f6c8eb9` |
| Rodinia candidate source | `/tmp/decoupled-rodinia-batch.KpLPSn` (not a Git worktree; source identity must be recovered before formal readiness) |
| E2 launch gate | M5.2 PASS plus revalidation of the frozen common formal anchor |

The CUDA SDK and Parboil entries above are only discovered candidate source
trees.  No executable, PTX, input, output-reference, or launch identity has
yet been frozen from them.  The existing framework launch definitions in
`util/job_launching/apps/define-all-apps.yml` are useful provenance leads, not
E1 acceptance evidence.

## Per-workload identity inventory

`PENDING_FREEZE` means the required field has not been asserted.  It does not
mean that a build or simulator run was attempted.

| workload | suite | source commit | wrapper/build | executable SHA | PTX SHA | input SHA | output checker/reference | launch geometry | provenance status | formal-ready status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BlackScholes | CUDA SDK | candidate `b7c5481c…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | candidate source located; Black-Scholes option pricing metadata corrected | NOT_READY |
| convolutionSeparable | CUDA SDK | candidate `b7c5481c…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | `--size 3072` candidate only | candidate source located | NOT_READY |
| fastWalshTransform_11_19 | CUDA SDK | candidate `b7c5481c…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | `-logK 11 -logD 19` candidate only | candidate source located | NOT_READY |
| scalarProd_13920 | CUDA SDK | candidate `b7c5481c…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | `--size 13920` candidate only | candidate source located | NOT_READY |
| scan | CUDA SDK | candidate `b7c5481c…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | candidate source located | NOT_READY |
| sortingNetworks | CUDA SDK | candidate `b7c5481c…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | candidate source located | NOT_READY |
| transpose | CUDA SDK | candidate `b7c5481c…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | `dimX512 dimY512` candidate only | candidate source located | NOT_READY |
| vectorAdd_6000000 | CUDA SDK | candidate `b7c5481c…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | `--size 6000000` candidate only | candidate source located | NOT_READY |
| cfd_097k | Rodinia | PENDING_RECOVERY | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | non-Git candidate tree only | NOT_READY |
| btree | Rodinia | PENDING_RECOVERY | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | framework candidate: `file ./data/mil.txt command ./data/command.txt` | non-Git candidate tree only | NOT_READY |
| dwt2d | Rodinia | PENDING_RECOVERY | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | non-Git candidate tree only | NOT_READY |
| gaussian | Rodinia | PENDING_RECOVERY | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | non-Git candidate tree only | NOT_READY |
| hotspot1 | Rodinia | PENDING_RECOVERY | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | non-Git candidate tree only | NOT_READY |
| lud | Rodinia | PENDING_RECOVERY | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | framework candidate: `-s 256 -v` | non-Git candidate tree only; review-promoted primary | NOT_READY |
| bfs | Parboil | candidate `4e0fc548…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | candidate source located | NOT_READY |
| cutcp | Parboil | candidate `4e0fc548…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | framework candidate: small `watbox.sl40.pqr` | candidate source located | NOT_READY |
| histo | Parboil | candidate `4e0fc548…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | framework candidate: default `img.bin -- 20 4` | candidate source located | NOT_READY |
| mri-q | Parboil | candidate `4e0fc548…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | framework candidate: small `32_32_32_dataset.bin` | candidate source located | NOT_READY |
| sad | Parboil | candidate `4e0fc548…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | framework candidate: default reference/frame inputs | candidate source located | NOT_READY |
| stencil | Parboil | candidate `4e0fc548…` | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | PENDING_FREEZE | framework candidate: small `128x128x32`, 100 iterations | candidate source located | NOT_READY |

## Acceptance and next scope

- No M5.E2 job has been launched, enqueued, or admitted.
- No unsupported feature may be accepted on the strength of historical traces.
- E1 remains incomplete until all 20 rows contain deterministic source,
  build, executable/PTX, input, output-check, and launch identities.
- The future Base/IO/OO job names are predeclared in
  `extended20/M5_E2_JOB_MANIFEST_TEMPLATE.tsv`; every row is explicitly
  `BLOCKED_M5_2_ANCHOR` and requires a fresh common-anchor recheck before it
  may enter a resumable runtime registry.
- Do not redo the approved 20-workload selection, and do not use the
  review-demoted `3mm` in place of `lud`.
