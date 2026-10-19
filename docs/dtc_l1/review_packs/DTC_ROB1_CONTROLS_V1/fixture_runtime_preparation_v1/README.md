# ROB1 actual LDST runtime preparation

**PREPARED_NOT_EXECUTED.** Source-only independent parent entry, pure classifier and six-case contract. No new module was imported/executed, fixture/test/compiler/simulator started, resource sampled or process signalled. Current build controller, Core and the parent's execution-source closure are unchanged. The coordinator now reports a completed actual matching ABI build; its build receipt SHA is `7cad272e1239b6c7f23cf897b44d455760e1308cb06bd6639bb06bdee39345d1`. ROB1 has not independently read/frozen the resulting ELF/library for this delivery. Their hashes in this preparation remain null, and this contract cannot release runtime.

`finite_ldst_runtime.run_registered(registration_path, expected_registration_sha256, cpu_admission_class=..., classify_output=...)` is a parent-only function, with no CLI. Parent copies/reviews this module and `evaluate_fixture_output.py`, prepares a distinct full-entry role, and pins registration bytes independently in its published entry. Inject the actual source-bound `CPUAdmission` (current API anchor `7268d0fb46f951ae51b9879988b89dd35c8dc9c4`, disk field `admission.disk_floor_exclusive_bytes`) and this pack's pure `classify`. Their source files and this launcher's actual path must appear in registration `source_sha256`; parent must include the complete imported gate/reviewer/ownership closure. This is a new `ROB1_ACTUAL_LDST_FIXTURE_RUNTIME_CONTROL` entry with exact parent Framework cwd, executable and full argv, not the existing external build role. Parent retains an outer start/terminal receipt even if registration/static-freeze validation fails before own output exists.

The required registration object is:

```json
{
  "status": "RELEASED_ROB1_SIX_ACTUAL_LDST_CPU_CASES_ONLY",
  "ordered_cases": ["omitted","explicit_zero","quota_one","bad_width","bad_mode","nonfinite"],
  "runtime_role": {"name":"ROB1_ACTUAL_LDST_FIXTURE_RUNTIME_CONTROL","cwd":"exact parent Framework cwd","executable":"exact Python ELF","executable_sha256":"parent-frozen digest","argvs":[["exact","full","entry","argv"]],"source_sha256":{"/absolute/imported/source":"parent-frozen digest"}},
  "source_sha256": {"/absolute/launcher/classifier/parent/gate/dependency/source":"parent-frozen digest"},
  "admission": {"disk_floor_exclusive_bytes":5368709120},
  "output": "/workspace/dtc-evidence-closure-20261019-v1/rob1/fixture-runtime-v1/attempt1",
  "static_freeze": {"path":"/absolute/future-static-freeze.json","sha256":"independently parent-pinned digest"}
}
```

This illustrates the schema; placeholders are not valid release data. The role must be the actual new parent entry, not this module (which has no CLI). `CPUAdmission` supplies all its unchanged host/cgroup PSI, 32GiB headroom, OOM and authority checks. Every one of the six cases obtains a new complete >=10.1-second pair; no reuse of a previous case's pair. Immediately before Popen, static source/runtime signatures are rechecked, runtime source hashes are reread and second-sample freshness must remain <=5 seconds. Admission output and actual fixture output must be on the same measured filesystem. A refusal stops this finite attempt without polling/retry. Each case gets an exclusive directory and a new own tmp; existing attempt evidence is never overwritten.

The future static-freeze JSON must have these exact fields:

```json
{
  "core_commit":"b1077667f7a2bcc72260733f88f5798f167346d1",
  "core_tree":"0a462efb9a48409064259735108b88dad127a53c",
  "core_source_manifest":{"path":"/absolute/all652-source-rows.json","sha256":"parent-frozen digest"},
  "actual_build_receipt":{"path":"/absolute/actual-build.receipt.json","sha256":"parent-frozen digest"},
  "compile_commands":{"path":"/absolute/actual-compile_commands.json","sha256":"parent-frozen digest"},
  "mapping_manifests":{"path":"/absolute/static-loader-manifests.json","sha256":"parent-frozen digest"},
  "fixture_sha256":"actual future ELF digest",
  "library_sha256":"actual matching whole libcudart digest"
}
```

Each source row is `{path: relative Git path, mode: "100644"|"100755", blob: Git blob OID, sha256: current expected byte hash}`. All652 regular Git leaves are assembled into a Git tree and must equal the fixed b107 tree; current files are checked by both SHA256 and Git blob OID, plus executable mode. Thus a claimed commit string alone cannot pass source closure. No Git command, compiler or ELF is executed. The successful actual build receipt must say matching Core, exit0, no reason, root reaped and no leftover group. Actual compile recipes for fixture/shader/gpu-sim require O1/g0, assertions enabled, fixture -UNDEBUG/-fno-access-control and no ROB1_ORIGINAL_CORE define. Static mapping JSON uses the existing mapping-role shape `{absolute_fixture_ELF: manifest}` with `target`, `interpreter`, `cache_mode=PRESENT_REQUIRED_EARLY`, and unique `files` containing full path/SHA/stat/role entries for the ELF, matching whole library, loader/cache and dependency closure. Parent must independently freeze actual PT_INTERP/DT_NEEDED/RPATH resolution and build IDs into its immutable static intake before release. The launcher rechecks each manifest file's SHA and full recorded stat identity before every Popen. This is static identity, not a claim that live mappings were observed. This fixture has no dladdr output, so no per-case loaded-library observation is invented.

The six fixed argv arrays are ELF + pinned original SM7_QV100 config + the three arguments in `FIXTURE_RUNTIME_CONTRACT.json`. All run without shell, with DEVNULL stdin, clean PATH/LANG/LC_ALL/CUDA_VISIBLE_DEVICES, exact own LD_LIBRARY_PATH and own TMPDIR. Maximum six roots, concurrency1, retry0;600 seconds total including admission/static checks/cleanup, a595-second work alarm with5-second cleanup reserve,60 seconds per case. Runtime checks actual output free strictly >5GiB; startup additionally budgets32MiB output and128MiB reserve (5,536,481,280 bytes). Output bound is sampled, not a filesystem quota. Root-only hard limits are CPU30/31s, AS2GiB, no core and512KiB per stream; sampled RSS<=1GiB and root tasks<=4. Any descendant is a failure. Other R2 thresholds are unchanged.

Only the current parent's retained direct Popen and pidfd establish ownership. Start receipts record actual root PID/start ticks/TGID/PGID/SID, boot and available live argv/exe/cwd; a natural terminal race is marked unavailable, never retried to manufacture a live observation. Exact unreaped root may receive pidfd TERM; wait is bounded at5 seconds and unresolved cleanup stops without fallback or peer/group signal. After reap only inspect/report session/group leftovers; never signal the remembered PID/PGID. Full source-bound resource/authority checks run during the case and once at final completion, even for a case that exits before the first live sample. OOM, disk, timeout, stream, source, authority or cleanup failures override expected output/negative exits. The classifier cannot authenticate arbitrary logs by itself.

The positive source asserts actual parser/default selection, real LDST constructor, four32B return packets in0/2/1/3 order for three requested collection sectors, ready edge11, first collection12, no same-absolute-cycle quota refill, preserved Ref1 through collection and denial, and one competing writeback's real RF-bank reservation. Omitted/0 finish collection12, deny WB13, retire14. Quota1 finishes14, denies15, retires16. Actual retirement clears active Ref/pending-write map, closes one ledger dependency and leaves lower outstanding/inflight empty. The final scoreboard emptiness is not independently asserted by this fixture. These are CPU component assertions, not native application values, architectural register checking or gpgpu_sim::cycle/kernel execution.

Each constructor negative must emit exactly `DTC_COLLECTION_QUOTA_UNSUPPORTED_STOP`, then the installed `gpu-sim.cc` SIGABRT crash-handler/backtrace signature, and exit1. A raw -6, arbitrary nonzero, assertion, SIGSEGV, timeout or resource failure fails. Negatives do not reach the collection/WB/Ref completion assertions. The three positive outputs require the exact single ROB1 trace record and exit0. This yields three actual-component completions and three targeted constructor rejections if actually qualified, not six positive results.

The original c809 fixture/header/library reference remains a separate, unregistered scope. This role forbids `ROB1_ORIGINAL_CORE`, old libraries and ABI mixing. Omitted/0 agreement here is not whole-binary OFF equivalence. No helper7 tests, canary, model/trace, performance selection or new simulation authorization is introduced. Parent must review/integrate, complete and pin static artifacts, register the independent runtime entry and receive separate release before calling anything prepared here.
