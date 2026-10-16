# V2: source-backed reconstruction and an isolated offline candidate

**Follow-up decision:** the user accepted research on this profile as an independent, clearly disclosed new derived candidate, without confirming original capture equivalence. The [current qualification review](../../DERIVED_INPUT_QUALIFICATION_CANDIDATE/README.md) supersedes the pending route-selection wording below. Historical capture binding remains unproven; it is no longer a prerequisite for the independent candidate. All HOLDs and launch restrictions remain.

Status: **SOURCE_PROFILE_AND_RAW_ADDRESS_CROSSCHECK_PASS; CANDIDATE_ONLY; EXACT_CAPTURE_BINDING_REVIEW_PENDING**. This is additional evidence, not an immutable receipt for the historical capture binary. Original Hotspot scientific promotion and admission HOLD remain in force. No simulator/GPU job, main parser change or registry edit was performed.

## Reconstructed instruction profile

The retained M5 CUDA11.8 sm70 ELFs were byte-identical but did not match the old trace (for example PC0040 is S2R in that ELF and IMAD.U32 in the trace). A retained AccelWattch artifact archive also contains a Hotspot ELF with sm70 code; it too differs (PC02a0 is NOP there and STS in the fixed trace). These were read/disassembled, never executed. See the [binary/prefix receipt](BINARY_AND_PREFIX_RECEIPT_V2.json) and [artifact member identities](ARTIFACT_EXTRACTION_V2.json).

The source bytes are identical in historical GPU-app-collection revision `40e0052cebd3f98006190ed09e78f4981ef1a41b`, the M5 source copy and the AccelWattch source: SHA `0f679be008be285d26ebd7d71eba47b164914dd52873c26ee63beecda2f68cc0`. A CPU reconstruction using CUDA9.1.85's PTX frontend and CUDA10.1.243's assembler produces a profile matching every observed PC and GPR signature in the fixed member. The direct9.1 build and9.1 PTX assembled with10.0 or11.8 do not match. This bounded comparison tests historical code layout; it does not identify the capture driver's exact JIT or claim that a newly built cubin is the original ELF.

[RECONSTRUCTION_RECIPE_V2.json](RECONSTRUCTION_RECIPE_V2.json) records commands, source/PTX/cubin/SASS hashes, host-header compatibility adjustments and resource usage. The reconstruction has32 registers and3072B shared memory, matching the original header. Only packages unpacked under this task's output directory were used; no driver or global CUDA installation was changed. NVIDIA package versions, official URLs/index identity and SHA256 checks are retained in the package receipts.

## Independent reference checks

The [full-profile check](SOURCE_PROFILE_VALIDATION_V2.json) verifies all13169524 warp records and377291004 active-thread instructions, covering185 observed PCs. It checks opcode **root** and ordered GPR destination/source lists against the reconstructed SASS. Predicate operands, instruction immediates and machine-code identity are absent from the trace and are not certified by that signature check.

The Rodinia source and matching SASS give an address model from CTA coordinates, a16×16 block, pyramid2 and the1024 launch recipe. This model is independent of the decoder formulas. It matches **16950260 explicit shared-memory lane addresses in660820 records**, plus **3720992 explicit global-load lane addresses**. The two input pointers agree with the original kernelslist memcpy addresses; output-store vectors independently yield one constant output pointer. All336608 active shared mode1 records have one encoder-compatible first-execution-lane anchor **under this source model**. No failed signature, raw-address comparison or anchor check was discarded.

The full GPR profile is in [SOURCE_PROFILE_PC_FORMS_V2.tsv](SOURCE_PROFILE_PC_FORMS_V2.tsv). Concrete shared-address witnesses from the first CTA also show that R18 is written once and reused by STS/LDS with different effective offsets. Register identity alone was insufficient before reconstructing those offsets. These witnesses and the raw-address checks support the source profile; they do not remove the separate capture-binding limitation.

## Candidate changes

The V1 inventory was deliberately conservative. Under this validated source profile, actual decoded differences occur only at six PCs:

| PC | Form | Changed records | Changed active-lane addresses |
|---|---|---:|---:|
| 0180 | LDG mode0 | 1364 | 23188 |
| 0190 | LDG mode0 | 1364 | 23188 |
| 0290 | STS mode1 | 1364 | 23188 |
| 02a0 | STS mode1 | 1364 | 23188 |
| 0ab0 | LDS.U mode1 | 58652 | 1425636 |
| 0ac0 | STS mode1 | 58652 | 1425636 |
| Total | | **122760** | **2944024** |

See [SOURCE_PROFILE_DELTA_V2.tsv](SOURCE_PROFILE_DELTA_V2.tsv) for first-occurrence identities and complete example address differences. Other mode1 records with a nonzero first printed lane often already decode correctly: their base is anchored at that same execution lane. Therefore a blanket lane0 or blanket active-ordinal rewrite is contradicted by the full-member check.

`util/dtc_l1/hotspot_format_candidate_v2.py` defaults to reporting. With an explicit `--candidate-output`, it creates a new derived file, rewrites only those six PCs when decoded addresses differ, and emits explicit mode0 lists. It requires the exact original input SHA and a passing source-profile receipt. Other records are copied byte-for-byte. It refuses existing output files and output locations in the raw member's directory; publication happens only after the final original SHA and exact change counts pass. It has no integration into the live parser or runner.

The candidate uses two independent references: the original full32-word raw vectors for mode0 LDGs, and the source/SASS address model for four shared PCs. Explicit-list round-trip checks run on every rewritten record. The parser/Core/runtime source remains unchanged. The eleven other fixed inputs are outside the tool's exact-member whitelist, and the live consumer still uses its original path; no all11 body rerun is required to establish that non-interference scope. This does not certify their historical producer semantics.

One consumer detail is included in that scope: after the frozen mode0 loop reads only the printed lanes, it attempts to parse `imm` from leftover words. Removing excess LDG address words can consequently change this unused parsed field. Frozen Framework18a68dcc `trace_driven.cc` (SHA `e82e9156bd28d61a044e1f677dc9e0e162290043404730ac9a81dae5ab402689`) reads `trace.imm` only for BAR, DEPBAR and WARPGROUP.DEPBAR behavior, not `LDG.E.SYS`, LDS or STS. Those control records are copied byte-for-byte. No equivalence of unused struct fields is claimed; the candidate's consumed behavior changes are the listed lane addresses. No other trace format is reinterpreted.

The local candidate and its receipt are review artifacts only. Their new derived input SHA must never be substituted into an old attempt identity. Before A uses this interpretation, review whether the matching source profile plus the independent raw-address checks are sufficient capture applicability evidence, or require additional original ELF/tracer/JIT/operand evidence. The existing twelve-row affected ledger still applies; corrected comparisons require new matched baseline/IO/OO attempts and only the controls actually used by a claim. Existing numbers remain original-model evidence.

The candidate is `/workspace/dtc-hotspot-format-174-v1/continuation-v2/candidate-source-profile/kernel-1.traceg`, SHA `21cd403581a94451e1f9e7a79950d7effd25319daccc101187233e4a0c985985`. [CANDIDATE_RECEIPT_V2.json](CANDIDATE_RECEIPT_V2.json) binds that output and all change counts. It is not registered or launched. Default report-only behavior produces the same digest without a trace output; protected before/after hashes and refusal checks are recorded in [VALIDATION_V2.json](VALIDATION_V2.json).

## Reproduce on CPU

Rebuild the source profile using the exact command arrays and package identities in the recipe. The local SASS path is `/workspace/dtc-hotspot-format-174-v1/continuation-v2/hotspot91-ptxas101.sass`. Run the profile verifier first, then the normalizer in a fresh separate namespace:

```bash
python3 util/dtc_l1/hotspot_format_source_profile_v2.py --member <fixed-original-member> --sass <reconstructed-sass> --output-dir <new-profile-directory>
python3 util/dtc_l1/hotspot_format_candidate_v2.py --member <fixed-original-member> --profile-validation <new-profile-directory>/SOURCE_PROFILE_VALIDATION_V2.json --report <new-report.json>
```

The second command reports the deterministic candidate digest without writing a trace. Creating a derived review copy additionally requires `--candidate-output <new-separate-directory>/kernel-1.traceg`. Neither command authorizes simulation or releases a HOLD. Raw traces, ELFs, cubins, package files and build directories remain outside Git.
