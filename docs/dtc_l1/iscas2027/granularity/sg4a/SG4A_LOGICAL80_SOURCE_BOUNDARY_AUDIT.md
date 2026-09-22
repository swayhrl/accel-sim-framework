# SG4A 80-KiB logical-Tag boundary audit

Audited Core/runtime: `95ccdb7a056f2d53f740d90869785cac6d4ee0f5` /
`462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9`.

Classification: `LEGAL_WORKLOAD_DEPENDENT_DEADLOCK_BOUNDARY`.

## Source findings

- `dtc-l1-common.h` constructs the Tag array as
  `logical_sets * logical_ways` and asserts only that logical sets, ways, and
  physical lines are nonzero.
- IO and OO both index Tags using
  `(line / kLogicalLineBytes) % logical_sets`; therefore 160 sets is legal and
  does not require a power-of-two geometry.
- Neither frontend imposes `logical_lines < physical_lines`.  At equal 640
  logical and physical lines, there is no guaranteed free physical-line slack.
  IO returns `NO_FREE_LINE` on an empty physical free list; OO can reclaim an
  occupied victim only when its reference count is zero.

## Immutable outcome and boundary

BICG and GESUMMV each deadlocked in both IO and OO at logical80.  The four
attempts are preserved in `SG4A_FAILURE_REGISTRY.tsv`; GESUMMV has no final
aggregate-stat checkpoint and is explicitly nonnumeric.  This establishes a
legal but workload-dependent forward-progress boundary, not an indexing error
or a basis for changing DTC semantics.

Do not launch further logical80 rows or substitute another capacity.  Continue
only the predeclared logical32/logical64 characterization; logical80 remains a
reported nonnumeric boundary.
