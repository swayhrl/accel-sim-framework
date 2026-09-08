# C11 acceptance matrix

Goal: `C11_C5_PREFILL_PROVENANCE_CLOSURE`

C11 is complete only when every REQUIRED item below is closed with evidence.

| ID | Requirement | Required evidence | Pass condition |
|---|---|---|---|
| C11-A1 | Import full prefill trace list | source path/hash, A checkpoint, C-owned copy/manifest | SHA-256 exactly `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`; no reorder/trim |
| C11-A2 | Import full decode1 trace list | same | SHA-256 exactly `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc` |
| C11-A3 | Bind immutable trace roots | per-entry existence + provenance | every list entry exists; source/archive identity recorded |
| C11-B1 | Trace prefill Weight allocation source | source/archive/sidecar audit | exact runtime allocation provenance established; not post-hoc guessed |
| C11-B2 | Trace decode Weight allocation source | same | authoritative runtime allocation provenance established |
| C11-C1 | Freeze modeled PA policy | `MODELED_DRIVER_PA_POLICY.md` | deterministic, non-performance-tuned, non-identity, placement-bit audit documented |
| C11-C2 | Build prefill C5 driver allocation | manifest/hash | full-page pinned contiguous model, no overflow/overlap, <=8 extents |
| C11-C3 | Build decode1 C5 driver allocation | manifest/hash | same policy and rules as prefill |
| C11-C4 | Generate prefill V2 registration | V2 artifact + validator | valid schema, nonidentity PPN, read-only, mapping class, ASID/epoch, <=8 extents |
| C11-C5 | Generate decode1 V2 registration | V2 artifact + validator | valid C5-specific registration; do not overwrite bounded C10B artifact |
| C11-D1 | Common PA mapping, prefill | directed mapping check | F0/conventional, F7 and F8 return the same modeled PPN for admitted Weight VA |
| C11-D2 | Common PA mapping, decode1 | directed mapping check | same |
| C11-D3 | Runtime eligibility independence | source/static/directed check | `OBJECT_WEIGHT` is telemetry-only; functional route depends on registration/access/context |
| C11-E1 | Freeze primary C5 fair matrix | `C5_ARM_MATRIX.tsv` | F0/F1/F2/F5/F7/F8/F9 present for prefill+decode; F7/F8 include Lseg 5/10/20 |
| C11-E2 | Preserve diagnostics discipline | matrix/labels | F6 optional diagnostic only; F3/F4 not misrepresented; H0 excluded |
| C11-E3 | Freeze exact configs | config files + hashes | every run point has deterministic config SHA and realized geometry/bits |
| C11-E4 | Freeze exact commands | `C5_COMMAND_MANIFEST.tsv` | no placeholder for required inputs; ROI/trace/config/registration/output explicit |
| C11-E5 | Freeze acceptance/conservation | `C5_ACCEPTANCE_MATRIX.md` | terminal, telemetry, exact-once, Segment/lower/PTE/cross-layer checks declared |
| C11-F1 | Preserve validated binary identity if no code change | provenance | Core `5b409493...`, binary `74307f...31345` retained exactly |
| C11-F2 | If plumbing code changes | commit/build/regression evidence | smallest behavior-neutral fix; affected focused + standard regression pass; new binary fully rebound |
| C11-G1 | No full C5 replay | process/evidence audit | no C5 performance workload launched |
| C11-G2 | No architecture drift | diff/review | no C9 capacity/topology/timing/fairness redesign |
| C11-H1 | Review pack complete | required files | all required C11 pack files present and internally consistent |

## Required final state

PASS only as:

`C11_C5_INPUTS_CLOSED_READY_FOR_C5_REVIEW`

A hard stop is allowed only as:

`C11_HARD_BLOCKER_WITH_EVIDENCE`

`READY_FOR_C5_REVIEW` does not authorize execution. C5 remains a separate user/review gate.