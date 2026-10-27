# Source authority and limits

## Authority chain

1. DTC selection: inherited `DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, 42 ordinary slots, 35 selected identities, seven conditional slots, two separate derived programs and 72 candidate input identities. Selection is preserved exactly.
2. Model comparability: inherited `MODEL_COMPARABILITY.json` is a separate scientific-model contract. This atlas neither reclassifies its accepted measurements nor uses performance to select source or inputs.
3. Source packaging: `/root/workspace/offline-sim-v1/accel-sim-framework/offline/manifest.lock` identifies GPU App Collection `dad09cb0487845edc7524ded814c6cde9f0ef6a1`. A lock declaration alone was not treated as proof.
4. Independent exact-byte verification: the GitHub connector read the [fixed upstream Git tree](https://api.github.com/repos/accel-sim/gpu-app-collection/git/trees/dad09cb0487845edc7524ded814c6cde9f0ef6a1?recursive=1), with `truncated=false`. The coordinator compared local source/header/Makefile bytes using `SHA1("blob " + decimal_byte_length + NUL + content)` against upstream blob IDs. All 1,443 existing relevant PolyBench/GPU, Rodinia and Parboil files match exactly. This is content provenance, not a claim that all 1,443 files were manually reviewed. `UPSTREAM_BLOB_INDEX.json` and `SOURCE_BLOB_VERIFICATION.json` retain per-file evidence and SHA256.
5. CUDA Samples: the suite agent separately inspects fixed [GPU App Collection b059fdae25c2aabf737486aada743fca114469ce](https://github.com/accel-sim/gpu-app-collection/tree/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2), recovered SDK4.2 files and relevant host differences. Never substitute an arbitrary recent CUDA Samples version for the historical trace. Per-report source citations specify the exact variant.
6. EP-L2: its independent historical scientific input contract, acceptance projections and per-member content hashes determine its lineage. Its candidate/shared asset library is not automatically the scientific manifest. See the cross-project mapping and EP-L2 view for exact scoped authority.

`AUTHORITY_RECEIPTS.json` records hashes of the inherited selection, model, source-index and adjudication evidence read by this audit. The published atlas fixes its own reports and copied source evidence in Git; it does not retroactively manufacture capture provenance.

## What is not established

The DTC freeze explicitly sets `exact_capture_executable_and_original_input_linkage_newly_certified=false` for every program slot. Source/ELF/input SHA fields that belong to simulator builds or native onboarding are not automatically benchmark capture-ELF bindings. Current executable existence or source-equivalent geometry cannot close this gap. Full-application numerical correctness remains distinct from declared-grid compatibility.

Trace reads are limited to command lists and bounded header prefixes, plus already accepted small metadata. Large instruction bodies and active raw results are not rescanned. Copied source evidence is solely for reproducible source review; it is never installed into an active benchmark build.

## Citation convention

A claim must identify a fixed repository commit, relative source file and line range, or an exact source-file SHA256 when upstream ancestry is unknown. Line numbers refer to the inspected byte variant. Reports distinguish candidate implementation from capture identity. For upstream-matching local files, the local absolute path is an access locator; the fixed GitHub commit is the identity anchor.

No same-name equivalence: Parboil SGEMM differs from PolyBench GEMM; Rodinia2.0-ft differs from3.1; Samples SDK4.2 and later parsers may change host dimensions and iteration counts. EP and DTC composite digests can use different canonicalization; compare member identities under the relevant hash formula.

## Separate M5 build and repaired variants

The additional [PolyBench build-variant audit](contributions/polybench/BUILD_VARIANT_AUTHORITY.md) reads fixed framework build/capture scripts and identifies a separate sgrauerg/polybenchGpu source anchor. Its ATAX, MVT, 3MM, GESUMMV and SYRK source/build details differ from the recovered collection candidate, including initialization fixes, block dimensions, coefficients and a capture-only GESUMMV transformation. These are versioned alternatives, not proof that any selected historical ELF contains the recovered candidate defect. Selected NVBit1.4/tracer3 metadata is not automatically bound to a later NVBit1.8 M5 recipe. Per-program reports retain these differences and the unresolved capture-time source/ELF chain.

Exact upstream source snapshots intentionally retain original whitespace; atlas-local attributes disable whitespace diagnostics and text normalization only for these immutable evidence snapshots. Authored reports, tables and tools retain normal checks.


## V1R1 field disambiguation

The separate V1R1 [schema](EVIDENCE_SCHEMA_V1R1.md) distinguishes registered trace identity from original input numeric bytes, and application capture ELF from simulator binary. Legacy V1 field names and findings are preserved as historical observations, not silently overwritten. Source candidate matches do not imply capture source/ELF linkage; older PolyBench M5 variants remain independent of selected NVBit1.4/tracer3 registrations.
