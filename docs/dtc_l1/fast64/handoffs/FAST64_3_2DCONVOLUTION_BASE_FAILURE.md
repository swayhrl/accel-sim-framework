# FAST64.3 — 2DConvolution/Base failed-attempt record

Status: **FAILED ATTEMPT PRESERVED; NOT A FAST64.3 RESULT**

The immutable historical-Core attempt
`fast64_3_2DConvolution_base_cap8192_a1_v2` naturally reached its terminal
receipt at `2026-09-10T12:50:39Z` with exit status `1`; it is not live and must
not be restarted, relabelled, or promoted.  Its immutable attempt UUID is
`844f1ba7-58a9-4208-98e5-71e01b1a6885`, Core/runtime are
`bbcbb5e...` / `6a8743b4...`, and its exact trace-list SHA-256 is
`23bcc08b04d82fc527ffc1365d3199f4d1f3057bf6a2705d1110c5c226227d64`.

The raw terminal diagnostic proves a simulator deadlock, not a timeout: after
approximately 2.33M current-grid cycles it reports no instruction commits on
cores 3, 29 and 51; 129 L1D latency-queue fetches remain
`MEM_FETCH_INITIALIZED`, with reserved conventional-L1 ways and reservation
retry diagnostics.  The runner captured a SIGABRT backtrace after the
deadlock detector, with no output/checker verdict available.

The adopted zero-access change is source-inert for PAPER_BASE because its
outer predicate is IO/OO-only.  Therefore a blind repaired-Core rerun cannot
be represented as a repair for this Base deadlock.  The next action is
source-backed root-cause/reproduction analysis of the conventional Base
reservation/lower-progress path; only an identified source-correct remedy may
create a fresh replacement namespace.  FAST64.3 remains ACTIVE.
