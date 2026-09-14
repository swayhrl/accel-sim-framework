# Obsolete and diagnostic material

The following classes are retained as historical material but are not an
execution dependency of the new 109 -> new174/2239 -> 164 pipeline:

- Old AutoDL bootstrap, retry570 capture, recovery-publish, and transfer
  helpers: host- and SM86/driver-specific reference only.
- Filesystem copies of `lane_g` under recovery staging and exchange packages:
  archival mirrors; Git is the code authority.
- R4 quantitative artifacts: `MECHANISM_ONLY`; they must not be promoted to
  R5 authority through this handover.
- Returned NSYS/NCU/NVBit diagnostics in exchange: `DIAGNOSTIC` unless a
  specific receipt declares their formal role. They are not a reason to retain
  old174 as a live runner.
- `Qwen3-30B-A3B` recorded metadata source: `UNKNOWN`, deliberately excluded
  from the current campaign scope; no inference is made from its filename or
  partial metadata.

No item in this section is a deletion candidate in this review.  Cleanup, if
ever authorized, must start from a separately approved, hash-closed retention
manifest and must not change immutable scientific evidence.
