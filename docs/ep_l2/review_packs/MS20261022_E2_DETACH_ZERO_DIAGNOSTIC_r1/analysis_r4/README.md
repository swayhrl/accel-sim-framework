# Final normalized observer numeric projection

This adds the missing exact212 counter projection to the existing E semantic
consumer. `legacy_semantic_report.py` is an unchanged copy of the reviewed
consumer. No decoder, simulator, controller, registry or source is modified.

After the original runner produces the complete normalized JSON:

    python3 project.py /path/to/normalized_summary.json --out provisional_projection.json

After E actually accepts the diagnostic point, populate `context_template.json`
from that E record, including its exact identity/references and the canonical
SHA256 of the whole normalized JSON (the provisional report prints this hash):

    python3 project.py /path/to/normalized_summary.json --context accepted_context.json --out accepted_projection.json

The accepted-context structure and diagnostic scope are consumed using the
existing reviewed semantic consumer. The additional checks bind that context to
this normalized summary, source/main/Q. They do not verify external files or grant
acceptance. Without that context, numerical observations remain explicitly
PROVISIONAL; synthetic input never grants application conclusions. The schema is
r4 production-source identical to r3; r4 fixture repair is not an additional
application policy. Existing source/qualification evidence remains authoritative.

All212 counters are emitted exactly once per global/available physical-slice
panel, with their source-domain/unit and explicit same-population denominator
where defensible. New40 capacity/joint fields use their measured populations,
not products of marginals. Every missing counter is null/UNKNOWN. A zero
denominator gives null ratio, never0%. Population-wide capacity checked/unobserved
and predicate-specific fail/checked ratios stay separate. Eligible-only predicate
checked counts are not emitted: eligible failures are reported over eligible
capacity-consulted heads, not mislabeled as predicate-checked failure rates.

Traditional line unobserved includes source-proven M1/existing NA. This script
retains explicit NA count and never adds it to unobserved or rewrites it as PASS.
Way first reasons have all-way denominator; predicate masks use live-way exposure.
No combined stall share, head-to-commit equality, response-to-transaction ratio,
later retry inference, sample extrapolation or performance claim is calculated.

The frozen decoder exports global and64slice counters and only phase catalog,
not numeric phase counters. Therefore this tool emits phase numbers UNKNOWN.
This one-kernel SGEMM diagnostic can be numerically explained at global/slice
scope; no phase expansion is required for launch or acceptance. Physical active
kernel phase is never causal request/victim kernel ownership. Original raw phase
records remain available for a separately bounded future consumer.

`result_template.json` contains null placeholders only and is not a result.
`CONTROL_RESULTS.json` records23 bounded Python metadata controls; these are not
native tests, app executions, observer validation or qualification. Some control
inputs deliberately isolate projection behavior and assume upstream arithmetic;
this tool does not reimplement decoder counter equations/terminal validation.

    PYTHONDONTWRITEBYTECODE=1 python3 test_project.py

The old SGEMM empty-fallback and old FWT whole-epoch store exclusion explanations
remain tied to their original evidence. New SGEMM positive RO proof cannot
retrofit dynamic evidence into old endpoints; old other-positive-RO causes remain
UNKNOWN. Source capture/source-off/native/drain validation stays with E/A2.
