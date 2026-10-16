# Remaining paper-critical evidence

The paper prose and raw-bit account are deliverable now. Missing performance
does not block those deliverables. Each later promotion creates a new pack
revision; this r1 must not be overwritten after publication.

| Priority | Owner / required artifact | Claim / table unlocked | Acceptance condition |
|---|---|---|---|
| P0 | Lane 1 INTERFACE_CONTRACT_V1 and BASELINE_CONTRACT_V1 | C08/C09, exact mode/config table | Exact source/binary/config/vector; finite WBUF + data carrier + copy/Bank semantics and all-OFF equivalence |
| P0 | Lane 5 independent correctness receipt | Production correctness, new main table | Data/version reference, same-address sectors, stale ID, rollback, Bank conflicts, backpressure, epoch drain; lifecycle/request checks pass |
| P0 | Lane 5 B16_BANKED/U_WB16 manifests + CSV | First mechanism effects | All five predeclared development workloads; same-source/binary controls, equal 1168-slot/4×292 budget, real WB control bounds, no hidden headroom; failures/slowdowns retained |
| P1 | Lane 5 static repartition + copy-cost control | Capacity vs copy attribution | Representative point after benefit appears; same total slots/Bank service; compute-only reference explicitly gives up bypass |
| P1 | Lane 2 module/integration and Lane 5 TVD data | C10, read-forward and avoided traffic | Sector-valid reads, atomic promotion, dirty forward reachable, actual extra retention and lookup/Bank costs |
| P1 | Lane 3 oracle/classifier/transaction proof + Lane 5 results | C11, conditional RO claim | Whole epoch hash/coverage/exclusions, concurrent write uncertainty rejected, duplicate read amplification and finite completion storage |
| P1 | Lane 4 diagnostics with exact ideal vector/receipts | C12, separate ideal table | Targeted blocker proven non-binding; historical 1152/static rows not relabelled B16 |
| P1 | Matched changed RTL, process/corners/macros/constraints | Differential area/delay/energy | Same constrained baseline/candidate; tools and reports retained, no software-size substitution |
| P2 | Lane 5 C8 and btree/dwt2d validation | Sensitivity and validation | Preset configurations/sets; scan queued separately and missing scan not imputed |
| P2 | Approved related-work sources and target venue format | Novelty/context and final typesetting | Primary sources verified; venue rules confirmed without inventing dates/page limits |

Existing historical calibration, M1 equivalence, M0b prefinal and Streaming
prefinal evidence are pinned in SOURCE_EVIDENCE_MANIFEST. Locally completed
but unarchived/ignored Streaming 13-row tables are not silently promoted here.
Historical source refs and compact-pack lineage are retained as historical
evidence; they do not meet the new B16 run-key by mere workload equality.

## Cross-lane result consumption

At stage boundaries fetch only the lane refs being consumed. Bind receipt
publication commit and file SHA256, then bind every result CSV, runtime
manifest and raw-log identity named in it. `plot_verified_results.py` accepts
a compact adapter JSON described in `RESULT_INPUT_CONTRACT.md`; the adapter
does not alter upstream CSVs. It fails closed on missing lineage, empty or
non-explicit vectors, non-complete rows, inconsistent controls or a shadow
row in an implementation dataset. A rejected input is not plotted as zero.

READY_FOR_REVIEW for this document pack does not mean the absent mechanism
results or physical PPA have passed independent review. Follow-up requires
the listed publications, not a background promise from Lane 6.
