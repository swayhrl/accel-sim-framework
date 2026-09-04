# M4I-RF0 range-index and object-coverage audit

Status: `PASS`.

The accepted archive and global VA evidence remain unchanged.  This audit only
checks the runtime-range object classifier before its result is used for M4C
observability or Weight segment registration.

| ROI | sidecar SHA256 | merged ranges | historical starts monotonic |
| --- | --- | ---: | --- |
| prefill | `8b605b8b19034613106a61ab993dcab60b6eb34509293074b123b44ceeaa839a` | 5 | PASS |
| decode1 | `7a07d6715fe79abd24cfc0b12d2619555e0bf472f5285781e098940acefccaa7` | 6 | PASS |

The historical sidecars happen to place the one contiguous Weight interval
below all ROI-admitted KV intervals, so the old merged lists are monotonic for
these exact immutable inputs.  The accepted Track-B object totals therefore
remain valid historical evidence; no full object rescan is required.

The integration analyzer nevertheless repairs the unsafe general case:

- same-kind ranges merge locally, then all resulting ranges sort globally by
  `(start, end, kind)` before binary-search indexing;
- `RangeIndex` explicitly rejects non-monotonic starts;
- decoder self-tests now exercise both KV-below-Weight and KV-above-Weight;
- resumable partial identity now binds the analyzer revision, schema
  `m4i-range-index-sorted-v1`, sidecar SHA, ROI, and the exact ROI-filtered
  global range map.

The corrected analyzer and resumable runner source blobs are respectively
`57d3cf1c249a2760cd67f0fafd5918037069c75b` and
`60998d56811b2db679e15aa52a7346a1eccd08b9`.  Python compilation and the
decoder self-test pass.  A one-trace resumable integration smoke completed
with its contract identity and a single processed trace; its prefill contract
SHA is `08bd106f6597865e622465ee3bd13233f7d49fd1eef131965fd2692956091e7a`.

No capture was recaptured, no raw trace was changed, and no range pattern was
inferred from accesses.
