# Independent E native replay draft and sealed intake

`replay_native.py` is a draft only. It has not compiled, linked or executed anything. No `E_NATIVE_INTAKE.json` has been invented. Root E must review the final formal A producer, prepare the real intake at the **root capacity pack** as `E_NATIVE_INTAKE.json`, pin its exact SHA256, and explicitly invoke the draft with both `--execute-sealed-intake` and `--intake-sha256`. The intake path cannot be redirected by a command-line argument.

The intake is the sole authority to select this finite native suite. It is not a new campaign or controller, and it cannot issue application starts. The original Coordinator admits exactly one E `test` lease, using original `REGISTRY.lock`, reserving 1 CPU, 8 GiB RAM and 512 MiB fully counted new-result growth. The original controller must be STOPPED, its old exact PID/start identity absent, its existing lock independently available, and the 36 historical charges/attempts/accepted endpoints/pairs/HOLDs unchanged. There is no `unique_controller()` call and no second controller or lock file.

The script enforces 1,800 seconds for the finite suite, with each compile/link/native case explicitly bounded to120 or300 seconds and shortened to the remaining suite time. New native work stops after the first failure or unresolved exit; no automatic retry occurs. The output directory is unique, previously absent, on the workspace device and under the original counted E result root. Existing logs/results are never overwritten or removed.

The real index requires these fields:

| Field | Required content |
| --- | --- |
| `schema` | `E2_CAPACITY_FORMAL_NATIVE_INTAKE_V1` |
| `status` | `FORMAL_PRODUCER_READY_E_INDEPENDENT_NATIVE_PENDING` |
| `sealed_by` | `E` or `E2` |
| `authority_commit` | `49343880865edb22a17523790fc32dd55975966c` |
| `production_main_or_archive_build_requested` | `false` |
| `source_identity` | Actual new Core/Framework/vendor commits and production `binary_sha256`; main61 is rejected |
| `core`, `runtime_framework` | Exact clean worktree paths matching those frozen commits |
| `formal_producer` | Actual `commit`, `release` and `remote_readback` content references, plus `formal_release_reviewed_by_E=true` |
| `main`, `archive` | Exact separately published production artifact references |
| `build_pins` | Nonempty list of actual source/build/link/environment/manifest evidence references |
| `test_elfs` | Finite ID→artifact mapping described below |
| `compile_steps` | Optional finite ordered list for independently building E test fixtures only |
| `cases` | Finite nonempty ordered native case list |
| `output_directory` | Unique previously absent absolute directory under original E result root |

A content reference always contains real absolute `path` and exact `sha256`. The script checks all current bytes. The actual release's local bytes must also equal its blob at the exact producer Git commit; the hashed remote readback must name that same `remote_commit` and nonempty `verified_paths`. Source HEADs must match and remain clean. Candidate source/build preparations and old main61 qualification are insufficient. Intake/source/artifact pins are checked before every stage by stable filesystem identity, with full content hashes rechecked at suite completion. Every directly executed fixture ELF is independently hashed immediately before execution.

Each `test_elfs` artifact has the content reference fields, `role`, `source_identity`, nonempty `source_pins` references and a real `link_provenance` reference. `bounded_fixture_source_reviewed_by_E=true` records the owner's source review, and at least one pinned C/C++ source must be a real Core `tests/ep_l2` fixture or an E pack `test*` source. Simulator main source cannot satisfy that requirement. New fixtures use role `NEW_PRODUCTION_NATIVE_FIXTURE` and exactly the new formal source identity. An optional producer-declared old OFF comparison fixture must instead use role `OLD_OFF_COMPARISON_REFERENCE` and `reference_only=true`, with its actual original artifact/source provenance. Such a reference is only bounded equivalence evidence and cannot become new-runtime or application qualification. Neither actual new main path/SHA nor old main61 SHA may be selected as a native fixture ELF.

Each native case has a safe unique `id`, exactly one `elf_id` or `generated_elf_id`, literal string-list `args`, exact integer `expected_exit`, a nonempty list of exact literal `required_terminal` markers, explicit `timeout_seconds` equal to120 or300, and `full_application=false`. No shell is inserted and `-trace` execution is prohibited. The selected native ELF itself is passed to `durable_exit.NativeProcess`; a Python/shell/checker process cannot stand in for its exit. Required marker checks are necessary together with the real native exit, not substitutes for it. Negative legality cases may specify an exact intentional exit; any resource/supervision stop still fails regardless of that integer.

Optional E test compilation/linking also runs through the same supervised single lease, directly executing a pinned compiler ELF. Every step has a safe unique `id`, `kind` (`COMPILE_E_TEST` or `LINK_E_TEST`), compiler reference, literal `args`, nonempty E-owned `source_pins`, optional `input_pins` for formal archives/headers/link dependencies, `timeout_seconds`120 or300 and `output_relative_path` ending in `.o` or `.native`. Exactly one `-o` must target that step's unique owned result subdirectory. Compile-only commands require `-c`; link commands must consume the actual E fixture source or a generated object. The script rejects build-system/parallel-build flags and production main/archive targets. It never invokes A CMake or builds a production simulator/archive.

The only argv substitutions are `{OUTPUT}` for the unique native result directory and `{STEP}` for that command's unique stage directory. Other substitutions are rejected. Root must pin and review every real config/include/archive/link input used by those literal commands. E fixture sources must live inside this E capacity pack. Generated test objects/ELFs do not receive a fabricated advance SHA: actual compiler exit and output SHA are recorded first, and `generated_elf_id` selects that exact newly measured artifact afterward. Production artifacts remain read-only inputs.

For each stage, `NativeProcess` creates the real stopped native child and durable ready record. E binds the lease to the native ELF PID/start ticks/boot ID **before** `release()`; the collector is its true wait4 parent. Outputs preserve ready/request/release/exit receipts, raw log SHA and required marker results. Real native wait/exit, PID/start ticks/boot ID, guardian identity, stop reason, exact command and artifact pins are copied into `CASE_RESULT.json`. No case becomes a formal application result or adds an application charge.

Each request and case report receives a separate deep copy of `bounds` and `binding`; subsequent cases cannot mutate old saved limits. The carried resource guard contains the real current 5 GiB workspace floor plus2 GiB monitor allowance, Share40 GiB floor, host64 GiB memory floor, 8 GiB owned process-tree cap, timeout/intake freeze, and approved cumulative new10 GiB/old+new24 GiB limits. All temporary/cache/compiler output stays within counted owned stage directories. The suite's512 MiB allowance includes all test artifacts/logs;16 MiB is retained for exit/metadata closure. High I/O alone creates no new stop threshold.

After a native exit, any remaining members of that exact native-owned PGID/session trigger owned-group termination and failure; no other project is selected by name. Missing constructor/exit/lease closure preserves evidence and leaves the original lease active for precise owner reconciliation rather than claiming exit0 or silently freeing resources. A safely closed run releases its original test lease. The final `NATIVE_REPLAY_RESULT.json` preserves every case and states `NATIVE_EXPECTATIONS_MATCH_PENDING_SCIENTIFIC_QUALIFICATION` only when exact execution checks match; E must still review assertion coverage and create the new scientific qualification separately. Failure or incomplete evidence remains explicit. Original T0, all36 charges and accepted results/pairs/HOLDs must be identical afterward.
