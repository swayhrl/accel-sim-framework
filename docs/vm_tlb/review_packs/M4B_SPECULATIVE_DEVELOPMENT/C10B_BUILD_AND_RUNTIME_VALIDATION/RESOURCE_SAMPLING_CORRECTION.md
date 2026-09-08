# Resource sampling correction — V2 history and `C10B_AGGRESSIVE_PARALLEL_V3`

At `2026-09-08T03:17Z`, review of the C10B preflight shell function found
that its iowait sample used `/proc/stat` field 5.  In the aggregate `cpu` line
that field is **idle**; iowait is field 6.  Therefore the `iowait_pct` values
near 24–26% in the three C10B-2 entries from `03:06Z` through `03:16Z` do not
measure iowait and must not be used for a resource decision.

The rows are retained for provenance.  Their independently sampled
`MemAvailable`, `SwapFree` (informational), PSI and swap-counter fields remain
as recorded.  The `03:16Z` preflight also had `pswpin_delta=15`, which is by
itself a valid no-launch condition under the active-swap rule.

All later C10B resource quanta use field 6 for iowait, compute total ticks
over fields 2..NF, and continue to require a ten-second zero `pswpin` and
zero `pswpout` delta before a heavy operation.  This is a harness correction;
it changes no simulator source, C9/C10 mechanism, fairness arm, or scientific
gate.

## V3 preflight-parser corrections

The first two attempts to aggregate the final F8 preflight exited **before**
acquiring the heavy slot or starting a simulator. The first emitted memory and
I/O PSI values on separate lines; the second read fixed line numbers despite
the policy/timestamp header. Both are resource-harness parser defects, not
resource failures or simulation results.

The final V3 reader selects rows by explicit `begin`/`end` labels and uses
field 6 (`iowait`) over aggregate CPU ticks. It admitted and ran the bounded
F8 job at `05:10Z`. V3 records page deltas as MiB/s using the observed
4096-byte page size; SwapFree remains informational. No simulator source or
scientific configuration changed because of either correction.
