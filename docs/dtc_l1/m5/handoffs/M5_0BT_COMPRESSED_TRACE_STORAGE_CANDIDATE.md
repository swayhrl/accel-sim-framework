# M5.0BT — source-backed compressed trace-storage candidate

Status: **SOURCE_PATH_CONFIRMED; FORMAL_EQUIVALENCE_NOT_YET_ESTABLISHED**.

This is a storage-recovery investigation for M5-0BT-011.  It does not change
the frozen Paper platform, capture source/input/tracer identity, raw/grouped
trace content, cache/DTC mechanism, result registry, or current 2MM
archive-only transfer.

## Source evidence

The active Framework trace frontend's `PipeReader::OpenFile()` dispatches any
path ending in `.xz` through `xz -dc`, while ordinary `.traceg` paths use
`cat`; see `gpu-simulator/trace-parser/trace_parser.cc` lines 624--635.  The
same `kernel_trace_t` text/pipe path is explicitly documented for
`.traceg/.traceg.xz` in `trace-parser/trace_parser.h`.  Therefore an
individually XZ-compressed text trace has a source-backed parser route; this
is distinct from the separate NVBit `.tracez` format and from a compressed
tar archive.

## Candidate representation

`TEXT_TRACEG_XZ_DERIVED` would retain the original immutable capture bundle
and create a separate derived store containing one `.traceg.xz` object for
each original replay-required `.traceg` object.  The derived
`kernelslist.g` may change only the referenced trace filename suffix.  All
`Memcpy*` rows, ordering, invocation count, kernel metadata, geometry,
configuration, and original capture provenance remain unchanged.

It is a storage representation, not a new capture or workload.  The original
remote `tar.zst`, raw/grouped source bundle, `CAPTURE_RESULT.json`, and
original SHA manifests must remain preserved.  Never substitute a tar archive
directly for a trace file, convert to `.tracez`, or delete the source bundle
to make this candidate fit.

## Mandatory proof before any formal use

1. Create the derived representation in an isolated namespace from one exact
   immutable bundle; retain the original untouched.
2. For every trace file, prove `xz -dc derived.traceg.xz` byte-equals the
   source `.traceg`; bind original SHA-256, compressed SHA-256 and decompressed
   SHA-256 in a derived manifest.
3. Prove the derived `kernelslist.g` differs only in trace filename suffixes,
   with positional byte-identical `Memcpy*` records and identical ordered
   invocation/geometry manifests.
4. Run a same-Core/same-config/same-bundle Base/IO/OO sentinel differential
   against the uncompressed representation.  Require exact simulated cycles,
   dynamic instructions, parser-visible DTC/lower/dependency/traffic fields,
   final drains, and output/trace consumption; host wall time may differ.
5. Register any accepted derived payload with an explicit
   `trace_storage_representation` identity.  Existing uncompressed results
   may not be silently relabelled or mixed inside a triplet.

Until all five conditions pass, this is not a receipt shortcut and does not
close M5-0BT-011 or permit M5.0BT advancement.
