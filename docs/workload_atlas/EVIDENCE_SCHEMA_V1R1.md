# Workload Atlas V1R1 — evidence namespace and compatibility contract

V1R1 is a **non-destructive overlay** on immutable V1, commit \`6a2ffc00621630c6986d157a8e629a8c0a07c2b9\`. The original \`WORKLOAD_INDEX.tsv\`, \`ARCH_FEATURE_MATRIX.tsv\`, \`INPUT_TRACE_BINDINGS.tsv\`, input-selection manifest, accepted simulations and cross-project histories remain unmodified. The new machine-readable projection is [EVIDENCE_BINDINGS_V1R1.tsv](EVIDENCE_BINDINGS_V1R1.tsv).

## Separate the objects being certified

| New namespace/field | Meaning | What it **does not** establish |
|---|---|---|
| \`inspected_source_candidate\` | Fixed source code version inspected in Atlas V1, byte-verified where recorded | That exact source produced the frozen capture |
| \`capture_source_link\` | Documented chain from capture to original/prepared source bytes and build recipe | No inference from shared names, header geometry or later M5 recipes |
| \`capture_elf_link\` | Exact application ELF (or code-object equivalent) bound to capture-time source/config/ROI | Not simulator executable, GPU target label SM70 or recovered new ELF |
| \`simulator_binary_link\` | Separate project/epoch-specific simulation binary and core/library build evidence | Not the application capture ELF or a cross-project model-equivalence certificate |
| \`registered_trace_identity\` | Frozen/registered trace bundle and member identity; candidate and derived statuses distinct | Not complete original application, input values, or numerical correctness |
| \`original_input_bytes_or_generator\` | Original numeric input bytes, fixed data file, or exact deterministic generator/seed linked to capture | Not a trace logical input digest, geometry or HtoD byte count |
| \`trace_scope_evidence\` | Source/launch/header/bounded-body coverage assertions with their V1 labels | Not full trace-body rehash or full-application semantic completeness |
| \`runtime_evidence_from_atlas\` | Whether this source-only audit itself measured execution | Atlas V1/V1R1 creates none; project historical runtime receipts remain separate |

**Unresolved is not false and missing is not zero.** Source code, registration, application correctness and simulator termination are independent evidence dimensions. In particular, all 35 frozen ordinary programs have *registered selected trace identity*, while capture-source/ELF and original input bytes remain unverified. The nine CUDA Samples whose V1 generic \`INPUT_BOUND\` says \`UNRESOLVED\` still have frozen registered trace identities. V1's narrower ambiguity must not erase that registration or be promoted to raw input-byte certification.

## Projection rules

- \`IDENTITY_FROZEN\` (35): \`FROZEN_REGISTERED_TRACE_IDENTITY\`, \`UNVERIFIED_ORIGINAL_BYTES_OR_GENERATOR\`, \`UNRESOLVED_CAPTURE_SOURCE_OR_PATCH\`, \`UNRESOLVED_CAPTURE_ELF\`.
- \`UNRESOLVED\` (7): conditional candidate(s), no selected input or automatic promotion. Source auditing is still valid at its fixed **candidate** version.
- \`EXCLUDED_DERIVED_MODEL_CONDITIONED\` (2): preserved as nonordinary, not folded into the 42 ordinary slots.
- \`simulator_binary_link=PROJECT_SPECIFIC_SEPARATE_AUTHORITY_NOT_CERTIFIED_BY_ATLAS\` intentionally makes **no claim of absence** of already-published DTC/EP binary proofs. Inspect the project's immutable performance receipt for that dimension.
- Preserve \`legacy_INPUT_BOUND\` and \`legacy_BINARY_BOUND\` verbatim for backwards compatibility, and use the new columns for any V1R1 consumer.
- Every performance claim needs its *own* exact simulator/config/input identity and may not be inferred from this source atlas. No new runtime runs, recapture, or numerical certification are supplied.

## Project application

For EP-L2, the V1 \`project_views/EP_L2.md\` used \`BINARY_BOUND\` for simulator lineage. For DTC source reports it meant capture application ELF; those are **different namespaces**. Under V1R1, always write \`simulator_binary_link\` for EP main61/observer r4/r5 or DTC Core9eed lineages and \`capture_elf_link\` for the producer application ELF. Source/trace member equality across projects never implies simulator-binary equality.

An individual program can be one frozen trace but an initialization-only phase (heartwall), a host/ROI mismatch (convolutionSeparable/scan), or a conditional prefix (CFD/streamcluster). See [PROJECT_SCOPE_ADVISORIES_V1R1.md](PROJECT_SCOPE_ADVISORIES_V1R1.md); read the per-program report before attributing memory behavior to the capture.

## Phase evidence

\`KERNEL_PHASE_FEATURES_V1R1.tsv\` is a new *source-candidate kernel/phase index*, not a measured per-kernel performance table. A row states source behavior with a report anchor, captures the applicable phase/variant, and explicitly records whether that phase exists in the registered trace. Never aggregate its address footprints as runtime misses/hits/stall-cycle components; see the row's scope/evidence fields.
