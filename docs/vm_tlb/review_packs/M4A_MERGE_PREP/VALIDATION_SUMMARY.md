# Validation summary

## Completed before coverage closeout

- MP0: both frozen archive SHA256 values match their authorization anchors;
  zstd/tar and internal `SHA256SUMS` contracts were independently checked.
- MP1–MP2: semantic classifier self-test passes and full lists conserve their
  724/772 entries while exposing 32 header-confirmed NCCL records per ROI.
- MP3: exact decoder self-test passes list-all sparse masks, base-stride,
  signed base-delta, single-lane, non-memory, malformed, page-boundary, and
  ROI-aware Weight/KV fixtures.
- MP6: frozen parser bounded smoke binds all representative COMPUTE and NCCL
  samples plus corrected compute-only startup derivatives.

## Coverage closeout

`ADDRESS_COVERAGE.md` records the two complete streaming scans and their
artifact hashes. A pass requires both scans to finish with zero decoder
invariant failures and no Weight/KV object-kind overlap.
