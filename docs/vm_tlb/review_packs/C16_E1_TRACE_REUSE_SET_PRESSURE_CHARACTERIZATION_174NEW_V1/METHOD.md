# Frozen Method

Status: `PRE_RESULT_METHOD_V1`. No dynamic result is encoded here.

## Phase A — static qweight footprint and accepted set mapping

Enumerate every aligned 128-byte line in each of the 28 frozen sidecar
intervals. Map each numeric `MODELED_L2_GET_ADDR` address by directly compiling
and calling accepted Core address-decoding and L2 set-index functions. Do not
transcribe an address formula. Fail closed unless the exact Core and config
SHAs in `SOURCE_ANCHORS.json` match. Run L0/L14/L27 start/mid/last canaries.

Record per region: bytes, lines, subpartition counts, per-set line population,
distribution/skew, and all pairwise layer set overlap. Record total target
lines and preserve interval/tensor identity.

For B8, B16, B24, and BFULL, use exact integer line budgets at 128 bytes/line.
Record global lines and `divmod(global_lines, 16)` quotient/remainder allocation;
do not round a byte budget into a different line budget.

## Phase B — one-heavy-pass trace summarization

Read each of the 4,515 qualified postprocessed `.traceg.xz` files exactly once
in the formal pass. Stream decompression and parsing; never materialize an
entire trace in memory or write a decompressed trace copy. Start with 8–16
workers and raise concurrency only if node164 input I/O remains healthy.

Produce compact per-kernel summaries and sorted little-endian line artifacts.
At minimum preserve dynamic SASS instruction count, CTA count, decoded global
address references, all-28 target/outside-target address and 128B-line counts,
unique lines, per-target-class references, semantic/decode identity, and dense
accepted-mapper histograms for both all-global and outside-all-28 traffic.

After this pass, every later phase reads compact summaries only. A failed or
unvalidated partial kernel may be rerun, but no systematic second raw scan is
permitted.

## Phase C — per-layer reuse distance

For each layer 0–27 and transitions D1→D2 and D2→D3, the primary boundary is:

`previous last true reference to this layer's target region`
→ `next first true reference to this layer's target region`.

Use exact prefix/suffix reference segments at endpoint kernels plus complete
intervening kernels. Complete-instruction distance excludes the two
target-containing boundary instructions and is reported separately from exact
reference counts. Assert that no current-layer target reference occurs inside
the strict gap.

Also retain the formal semantic `up_proj` range start/end boundary and its
intervening metrics. Never silently substitute it for the true-reference
boundary.

Report elapsed kernel span, complete intervening kernels, dynamic SASS
instructions, global address references, all unique 128B lines, layer-relative
non-target unique lines, same-subpartition references, conflicting-set unique
lines, and the next reuse's actually referenced unique target lines.

## Phase D — set-conflict pressure

For every target set in every reuse gap, accumulate layer-relative non-target
line-reference and unique-line pressure using the accepted mapper. Report
median, p90, p99, maximum, hot-set fraction, per-layer rows, per-subpartition
distributions, and D1→D2 versus D2→D3 stability.

Label all such output `SET_CONFLICT_REFERENCE_PRESSURE_PROXY`. It is not an
eviction or cache-traffic observation.

## Phase E — quota interpretation

Join static placement and dynamic pressure for B8/B16/B24/BFULL. Report quota
fractions, exact per-subpartition quotas, target-set population relative to an
explicit even-per-set reference, candidate set-local pressure, highest/lowest
pressure layers, and the proxy condition “global quota sufficient but
set-local placement unfavorable.” State the rule used and keep
`actual_admission_denial_or_eviction_claimed=false`.

Do not infer a performance order among budgets.

## Formal validation gates

Before scientific interpretation, require:

1. exact trace manifest, sidecar, Core, config, mapper, scanner, and sequence
   identities with SHA receipts;
2. 4,515-kernel closure and trace-index instruction/CTA closure;
3. per-kernel all-global and non-target histogram-sum closure, including
   prefix/suffix boundary segments;
4. L0/L14/L27 accepted-mapper canary pass;
5. D1/D2/D3 coverage and all 56 layer-transition rows;
6. no raw-trace open by aggregation;
7. explicit claim-boundary fields in every dynamic output;
8. I/O/resource monitoring evidence for the formal scan.

Any failed gate blocks `SCIENTIFIC_INTERPRETATION.md` and the suggested final
label.
