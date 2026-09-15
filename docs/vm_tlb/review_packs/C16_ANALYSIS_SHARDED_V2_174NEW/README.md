# C16 Analysis Sharded V2 — 174-new

Decision: `ANALYSIS_SHARDED_V2_PASS`.  This branch starts at accepted analysis
prep commit `d07b7eb5d43b9a31474a6d298ec4e4f75292cc48` and implements V2
CTA/MREF shard analysis with a strict set-union-only merge boundary.

`analyze-logical-target` reads a `C16_LOGICAL_TARGET_MANIFEST_V1`, verifies each
cataloged child manifest and its artifact hashes, requires matching target
identity, parses children independently, and writes child and logical-target
receipts below `derived/`.  A CTA target can remain
`PARTIAL_SHARDS_PRESENT`; a claimed `MREF_SHARDED_COMPLETE_SET` fails unless its
declared MREF groups exactly cover the frozen selected set.

No node109 compact-binary record-layout/version specification exists in the
frozen V2 coordination head `268f93111c5343945f2b50c0d2c59820a1b6d702`.
The parser therefore exposes the explicit ready-hook token
`NODE109_COMPACT_BINARY_FORMAT_SPEC_REQUIRED` and rejects any unrecognized
binary source rather than guessing a layout.  It must be replaced with a
versioned decoder only when node109 supplies a hash-bound format specification.
