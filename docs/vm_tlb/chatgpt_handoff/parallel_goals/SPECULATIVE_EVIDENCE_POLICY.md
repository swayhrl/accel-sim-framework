# Speculative evidence policy

Status: **MANDATORY FOR WINDOWS B/C**.

## Labels

Every B/C artifact/result must carry one of:

- `SPECULATIVE_DIAGNOSTIC`: exploratory result, not formal evidence.
- `SPECULATIVE_CANDIDATE`: passed its local validation and may be considered for later promotion.
- `SUPERSEDED`: invalidated/replaced by later evidence.
- `FORMAL`: forbidden in B/C unless ChatGPT explicitly promotes it after review.

## Non-negotiable rules

1. B/C may reuse accepted immutable traces and accepted Core semantic baseline, but their results are not automatically M4C/M4B formal results.
2. A source/config/result mismatch never gets papered over by copying a formal label.
3. If a speculative run fails because of a local script/config issue, fix and rerun that arm; keep the failed run manifest as diagnostic evidence when useful.
4. Never tune parameters to reproduce a desired paper number.
5. A missing paper detail remains `UNKNOWN` or an explicitly authorized approximation.
6. Cross-window comparison is allowed only when the compared inputs/configs are clearly bound and semantic differences are listed.

## Required provenance per speculative simulator run

Record at least:

- window = B or C;
- run ID;
- evidence label;
- Framework SHA;
- Core SHA;
- simulator binary SHA-256;
- mapped simulator-runtime path/SHA when checked;
- trace policy and list SHA-256;
- object-map SHA-256 when used;
- complete materialized config SHA-256;
- ROI/workload;
- start/end/status;
- expected and started-kernel marker count;
- telemetry record count when enabled;
- output/log SHA-256 or stable summary hash;
- deviations from the accepted A configuration.

## Required validation before `SPECULATIVE_CANDIDATE`

For unchanged accepted VM semantics:

- normal exit;
- intended ROI/workload consumed;
- no request-conservation failure;
- zero PTE response misassociation;
- waiter registration/wakeup conservation where applicable;
- no duplicate store/atomic/data side-effect assertion;
- quiescent translation state when the run contract requires it;
- telemetry/object conservation when enabled.

For C mechanism changes, additionally satisfy `WINDOW_C_VALIDATION_CONTRACT.md`.

## Promotion policy

Promotion from B/C to the authoritative lineage requires:

1. ChatGPT/user review;
2. exact source/config semantics frozen;
3. any required rerun in an accepted branch/worktree;
4. a formal review pack that references, but does not silently relabel, speculative evidence.

The user has explicitly accepted that speculative experiments may be rerun after A/C4 corrections. Therefore B/C should favor useful coverage and early information while preserving enough provenance to know exactly what must be rerun.
