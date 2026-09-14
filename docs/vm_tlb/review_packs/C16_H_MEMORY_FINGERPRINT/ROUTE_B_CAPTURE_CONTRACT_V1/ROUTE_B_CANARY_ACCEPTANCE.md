# Route B canary acceptance

This is a future, explicitly authorized GPU procedure; it is not run by this
contract. Use one frozen selected candidate, one predeclared static subset, and
one bounded launch window. The canary must PASS all of:

1. Exact full-mangled function, model/runtime/scenario, code-object SHA, and
   static-map SHA match the frozen manifest.
2. The static map is nonempty and its selected subset has one or more explicit
   `GLOBAL && has_mref=1` rows; every row has a supported load/store/atomic
   access kind.
3. The exact kernel launches, has GLOBAL address-bearing rows greater than zero,
   preserves active-mask semantics, and preserves predicate semantics when a
   predicate field is available.
4. Per-lane addresses, width, access kind, launch identity, and terminal record
   satisfy `ROUTE_B_TRACE_SCHEMA.md`; no LOCAL/SHARED/UNKNOWN row enters a
   GPU-VA result.
5. Terminal status is `COMPLETE`, raw/map/manifest/output-checksum receipts
   close, and overflow/dropped-event counters are zero.
6. Measured raw size and elapsed time are within the predeclared bounded
   projection, 4GiB, and 20 minutes.

Failure or an unexpectedly high GLOBAL-MREF/dynamic-record count stops formal
capture. Before retry, freeze sorted static-index subsets A/B/C from the static
map and project each subset independently. They must be disjoint and their
union must reproduce all selected-function GLOBAL-MREF indices; result-driven
partitioning is forbidden.
