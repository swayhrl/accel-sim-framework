# Storage transfer plan — deferred after M0/V0

## Storage classes

| Class | V0 disposition |
|---|---|
| A. independently verified on destination | None proven.  Do not claim a destination model, runtime, NVBit build, or mount exists. |
| B. copy from source | Hash-closed 4080 NCU/U8 artifacts when their source paths are accessible, plus the explicitly approved 3090 minimum comparison subset. |
| C. immutable re-download/rebuild | Exact Llama revision only after identity/hash admission; CPython/wheelhouse, NVBit, tracer, and NCU environment only after destination verification. |
| D. 3090 historical comparison only | Q1/Q2 raw + static maps, six Route-A formal traces, and committed bridge/analysis products. |
| E. source-only | The full `/root/share/c16_recovery_v3` endpoint, host-private records, and non-selected archival material. |

## 4080 R5 long-term retention

- Retain outside Git: the N1 raw report (`d2e97a...07102`) and CSV
  (`372ee...56d17`), paired together; the U8 raw-run root with manifest SHA
  `6c801d...30f8e`; any subsequently located R5 U5/U6/U9 raw stdout/static-map
  payload only after it is bound to an existing receipt.
- Retain in Git: R5 review/receipt packs, runner scripts, static definitions,
  frozen-input admission script, NCU/NVBit tool source, and provenance docs.
- The exact Llama asset is *not* demonstrated as source-available by the
  U4 admission record.  Its required immutable revision is
  `4e20de362430cd3b72f300e6b0f18e50e7166e08`; obtain it only through a
  later approved identity/hash admission.

## 3090 minimal comparison subset

Do not copy the approximately 75 GB recovery root.  If Cache/TLB/AI workload
comparison is authorized later, copy-not-move only: Q1 raw; Q2 Prefill and
Decode raw and their static maps; six Route-A formal traces; and the Git
Route-A→Q2 bridge, Q2 anchor characterization, selection sensitivity, static
map/campaign receipts, and CUTLASS unresolved-identity closure.  This current
known-size raw subset is 763,868,911 bytes.  It preserves the frozen state:
Q1 PASS, Q2 Prefill COMPLETE, Q2 Decode COMPLETE, bridge PASS, 34/36 exact,
and two required CUTLASS rows FAILED_CLOSED.  It neither authorizes a canary
nor resolves representative selection.

## Future transfer closure (not executed in V0)

1. Bind the actual destination external mount; record it as a new destination
   receipt rather than editing this source plan.
2. Enumerate each source file from the manifest.  For pre-closed large files,
   use the cited existing SHA only after confirming the matching authority
   receipt; otherwise calculate source SHA/size.
3. Copy, never move.  Store raw/profiler/model assets outside Git.
4. Calculate destination SHA/size and require equality before marking a row
   transferred.  Preserve the source copy.
5. Do not transfer host-private records, secrets, or unrelated source assets.

No destination path is asserted beyond `TO_BE_BOUND_ON_DESTINATION`.
