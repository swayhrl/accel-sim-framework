# Lane-6 validation

Status: `PASS_LOCAL_DOCUMENT_AND_TOOL_CHECKS`; independent review pending.
No simulator tests, workload runs, candidate RTL synthesis or PPA measurements
were performed by Lane 6. The tests below validate provenance/plot intake,
not the EP-L2 cache implementation.

## Evidence producer

The exact documentation/tool producer commit is recorded in
`SOURCE_EVIDENCE_MANIFEST.json:generator_source.commit`. Runtime source fields
for new EP-L2 experiments remain absent; this commit is never a simulator
runtime authority. SOURCE_EVIDENCE_MANIFEST binds 23 exact historical,
contract, interface and dependency blobs by Git object identity and SHA256.

## Checks and results

| Check | Result / compact evidence |
|---|---|
| Actual prose and cost ledger | Written Chinese introduction/problem/architecture/method/PPA, claim map and unresolved evidence register |
| Offline generator | Four SVG/PDF figures, six accounting scenarios; `validation/FIGURE_BUILD.txt` |
| Reproducibility | Second generation into a fresh temporary directory: all 14 generated artifacts byte-identical; `validation/REPRODUCIBILITY.json` |
| Result intake | Nine tests passed; synthetic Git-bound receipt/bundle/CSV/manifests roundtrip preserves a 0.8× slowdown and rejects hash tampering; `validation/RESULT_INTAKE_TESTS.txt` |
| Evidence type rejection | Missing binary, empty vector, coordination-as-runtime, incomplete/data-check gates, oracle/ideal/shadow contamination rejected in intake tests |
| Independent budget arithmetic | 1152/1160/1168, 4×288/290/292; 9-bit descriptor ID and 6-bit 0..32 count; `validation/BUDGET_CHECK.txt` |
| Visual inspection | Rendered and inspected all four PDF figures through pdftoppm; axes, captions and workload labels legible; zero/slowdown samples retained |
| PPA honesty | Area/power/Fmax/generation width unfilled; historical RTL/tools discovered, no matched candidate delta synthesis claimed |
| Dependencies | Exact Lane-1/4/5 publication/receipt hashes in DEPENDENCY_SNAPSHOT; Lane-1 runtime_ready=false, new result manifests absent |
| Scope and integrity | Only Lane-6 report/review-pack paths; source/CSV inputs read with git show; staged diff check and SHA256SUMS verification recorded before publication |

The synthetic intake fixture creates a temporary Git repository, fabricated
test-only identities and temporary figures outside the review pack; those
rows are never used by the paper, manifest, or historical scientific figures.
Raw experiments were not rerun to make packaging uniform.

## Toolchain

`validation/ENVIRONMENT.json` records host, Python/Matplotlib/Git versions and
tool discovery. PDF/SVG metadata timestamps are omitted so regeneration is
stable within that environment. Mermaid remains editable source; no rendered
Mermaid timing/layout validation is claimed.

## Limitations of the check

Historical evidence is pinned to archived source/compact data, not requalified
as new B16 runtime. Passing intake protects lineage and comparison structure;
it does not replace reading producer semantics and Lane-5 scientific review.
The adapter intentionally refuses oracle/TVD comparisons until their exact
transition contracts are added in a later revision. No synthetic test proves
RO correctness, TVD correctness, physical SRAM area or timing closure.
