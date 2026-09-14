# C16-G Retry570 runtime status

Status: `C16_FULL_AUTHORITY_RECOVERY_V3_ACTIVE_PIPELINED_QWEN0_S3_PREDICATE_CLOSEOUT`.

## Latest independently reviewable checkpoint

`Qwen0 / S3_TEXT / R5 / PREFILL` is closed as `PREDICATED_OFF_TARGET`.
The direct NVBit-native map selected exact full `pytorch_flash::flash_fwd_kernel`
static index 8 (`@P2 LDG.E`, GLOBAL MREF); the immutable S3 forward launched
that exact function 24 times and reached 2,752,512 target callbacks, but
`predicate_true_count=0` and `nonzero_mref_count=0`.  This is neither a tracer
failure nor an address-zero/MREF capability conclusion, and it is not admitted
to R6.  The raw map/log are remote SHA-closed and `COPYBACK_READY` for Lane B;
the compact forensics SHA256 is
`62d9c607b17e5e311756beee679e16921516614a1c5bda75733f0c174be83205`.

The initial adapter-name setup failure is retained as a non-scientific
pre-model-load attempt.  It did not alter the model, input, target, or the
terminal predicate-off conclusion.

The retained S3 PREFILL map has now passed actual-code-object closure against
`/root/autodl-tmp/c16_retry570/venv_cp310_cu124_final/lib/python3.10/site-packages/torch/lib/libtorch_cuda.so`
(`761b14ac…ccb6a`), plus nonempty/exact-mangled/exact-code-SHA/unique-static-index
semantic validation (4,312 instructions; validation SHA256
`6e8f521933bcca52ba84498223631c94e2e1e2d18ad2180fbfe686bea1b07820`).
It remains `PENDING_R4_SOURCE_TO_R5_IDENTITY_JOIN`, not an accepted map PASS:
the retained R4 source catalog payload is currently unavailable, and a shared
ordinal alone is explicitly forbidden as a substitute join.

`Qwen2.5-0.5B-Instruct / S4_STRUCTURED / R3_NATIVE_BASELINE_AND_G1_CENSUS` is
`PASS_COPYBACK_READY`: 431.503 ms native median, complete 17.522 s G1 census,
and a retained 12,869,674-byte remote report with SHA256
`6a3d09fa4ad2ee7c794a65050a9e99a68c2d49382b829371d6d8544ae83bf964`.
Lane B owns local copyback/SHA closure.  Its formal window is closed.

`Qwen2.5-0.5B-Instruct / S3_TEXT / R3_NATIVE_BASELINE_AND_G1_CENSUS` is
`PASS_COPYBACK_READY`.  The frozen float16/sdpa/eager baseline completed with
475.763 ms median and 3,725,007,360 peak allocated bytes; its G1 nsys census
completed normally.  The retained remote report is 12,591,324 bytes with
SHA256 `246dbce102b43849365903bbedf71b81f73db92b3f5d75f5f387fd933e349782`.
Lane B owns copyback and local SHA closure; no raw payload is in Git.  The
formal window is closed (`MEASUREMENT_ACTIVE=absent`, GPU-process count 0).
The compact review receipt is
[`QWEN0_S3_TEXT_R3_CENSUS_COMPLETE.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_full_authority_recovery_v3/milestones/QWEN0_S3_TEXT_R3_CENSUS_COMPLETE.json).

`GPU_READY_QUEUE=[Qwen0/S3_TEXT/PREFILL_R5_V2_INDEPENDENT_REPRO,
Qwen0/S3_TEXT/DECODE_R5]`; `GPU_ACTIVE_JOB=none`;
`NEXT_GPU_JOB=Qwen0/S3_TEXT/PREFILL_R5_V2 independent repro`.

The immutable `S3/PREFILL/target-v1` index-8 result is closed only as
`PREDICATED_OFF_TARGET`; it is never to be rerun, widened, or rewritten.
It does not close S3, Prefill research, or the separately phase-authorized
Decode row.  The one permitted replacement is now frozen as
[`S3_PREFILL_TARGET_V2`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_full_authority_recovery_v3/milestones/qwen0_s3_prefill_target_v2/QWEN0_S3_PREFILL_TARGET_V2.json)
(`e8da35b57dc33e15c357abd834608bc9181dfd2ecccb92ed9edb8c781ce79806`):
the earliest unpredicated direct GLOBAL MREF in the same hash-closed exact
function is `STG.E.128` at static range `[4125,4126)`.  This is a new,
immutable target-plan version and not a V1 modification.  One bounded V2
discriminator is authorized; no third target scan is authorized after it.

That sole V2 discriminator has completed as
`COMPLETE_VALID_ADDRESS_BEARING`: its exact function launched 24 times;
`callback_count=predicate_true_count=active_lane_count=nonzero_mref_count`
was `2,752,512`, `zero_mref_count=0`, and every returned record carried static
index 4125.  It ran for 8.071 seconds under the campaign-scoped snapshot-bound
lease, with immutable `STG.E.128 [4125,4126)` and frozen output/backend
closure.  Its two raw payloads are remote-SHA closed and appended to the
single shared `COPYBACK_QUEUE` as `COPYBACK_READY`; Lane B owns copyback.  The
next GPU task is the one permitted independent repro using this unchanged V2
plan; Decode remains queued immediately afterwards.

The independent repro also returned `COMPLETE_VALID_ADDRESS_BEARING` under
the same frozen model/input/backend/target range: all 24 exact launches again
reported predicate-true, nonzero-MREF records.  Its raw map/log are likewise
`COPYBACK_READY`; next GPU work is now `Qwen0/S3_TEXT/DECODE_R5_STATIC_MAP`.

The fixed authority audit is
[`RECOVERY_V3_G1_AUTHORITY_AUDIT.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_full_authority_recovery_v3/milestones/g1_authority_audit/RECOVERY_V3_G1_AUTHORITY_AUDIT.json)
(`604fb22d3f57c665e7096d499e491440bf6e7a259b4db3cc1e5ff337e20bf307`).
It makes Qwen0/S1_CODE and Qwen7 raw S2/{TEXT,CODE,STRUCTURED} historical G1
claims `SUPERSEDED_NON_AUTHORITATIVE_REQUIRES_CAMPAIGN_G1`: the retained
baseline may be reused only after frozen-identity comparison, while a new
campaign-scoped parent-lease G1 must produce a real `.nsys-rep`, export, and
validated phase-linked catalog.  The historical ledger is immutable.

Unresolved Qwen0/S0 Prefill remains the separately closed
`STATIC_INDEX_FILTER_OR_DYNAMIC_EXECUTION_NOT_REPRODUCED` branch.

## Superseded historical narrative — non-authoritative

All historical claims of `Qwen0 S1 G1 COMPLETE`, `Qwen7 raw S2 G1 COMPLETE`,
and the old `GPU_READY_QUEUE_COUNT=3` below are retained solely as provenance.
They are explicitly `SUPERSEDED_NON_AUTHORITATIVE`; the live authority is the
latest checkpoint above and the fixed G1 audit.  They must not be scheduled or
consumed as Recovery-V3 G1 inputs.

## Current execution authority — v11 Qwen0 forensic / v10 pipeline (historical provenance only)

Current runtime source checkpoint: `2deb60af60bae849cec1b018b05091f70c9319ae`.
It adds only predicate-aware offline accounting and deterministic target-plan
materialization; the runtime model path is unchanged.  The code was focused-
test-passed and pushed before the resulting plan was used.

Qwen0 S0/PREFILL original corrected-tracer raw is retained and dual-SHA
closed.  Its D1 forensic receipt reports 72 trace files / 21,312 rows, exact
static index 45 and `LDG.E.LTC128B.CONSTANT`, 21,312 inferred active rows,
zero predicate-true rows, and zero address lanes counted under the required
predicate-true-only rule.  The correct classification is
`PREDICATED_OFF_TARGET`, not an address capture failure.  The immutable-map
replacement is static index 86 (`LDG.E.LTC128B.64.CONSTANT`, `[86,87)`) in
the same exact function.  Its one bounded canary completed checksum/backend
and measurement-window gates but emitted 72 header-only target traces with
zero dynamic rows.  It is retained as
`STATIC_INDEX_FILTER_OR_DYNAMIC_EXECUTION_NOT_REPRODUCED`, not as a second
MREF capability result; no further index scan or repeat is authorized without
new direct mapper evidence.  The independent prior repro remains retained;
no raw evidence was overwritten.

Pipeline progress independent of that Qwen0 root-cause branch:

- Qwen2.5-0.5B S1/CODE G1 nsys census is `COMPLETE`; its `.nsys-rep` is
  12,705,409 bytes and remote/local SHA256 is
  `810b990adcd5187bf0c9e64806b5d4ba646e8caadff6e45625f49cfa6e093a5d`.
- Qwen2.5-7B raw S2/TEXT native baseline and G1 census are `COMPLETE` for
  B1/T2048/Decode32, raw bf16/sdpa/eager.  The `.nsys-rep` is 26,180,948
  bytes and remote/local SHA256 is
  `c89efab03c9facf43c135445c6e3e62c5669f1ae9d12eefbbf156af1b9ce23cd`.
- Qwen2.5-7B raw S2/CODE native baseline and G1 census are `COMPLETE` under
  the same frozen runtime dimensions.  The `.nsys-rep` is 26,262,392 bytes
  and remote/local SHA256 is
  `b04aafcd746295414f053d8053da3863400ffa82519589738b5879f5307c9061`.

All three completed profiles used an exclusive remote
`GPU_IO_EXCLUSION.lock`; post-window checks found
`MEASUREMENT_ACTIVE=absent` and `ACTIVE_GPU_PROCESS_COUNT=0`.  Raw reports
remain exclusively under `/root/share/c16_recovery_v3`, never Git.

`GPU_READY_QUEUE_COUNT=3` (Qwen7 S2/STRUCTURED, Qwen7 S3/TEXT, Qwen0
S1/CODE follow-up).  `GPU_ACTIVE_JOB=none`; `GPU_UTILIZATION_STATE=between
exclusive windows`; `REMOTE_TRANSFER_JOB=Qwen7-AWQ model`; its rsync has
naturally completed but package-wide payload SHA closure is still pending;
`NEXT_GPU_JOB=Qwen7 raw S2/STRUCTURED native baseline`; `WHY_GPU_IDLE=only
post-profile SHA/publication boundary, not unrelated model transfer`.

## Active Recovery-V3 asset and runtime checkpoint

The prior post-Llama closeout below is retained historical evidence; it is not
the authority for the active Recovery-V3 campaign.  Recovery-V3 scope is the
v9 roster: Llama S1--S4, Qwen2.5-0.5B, Qwen2.5-7B raw,
Qwen2.5-7B-AWQ, Qwen3-8B, DeepSeek-V2-Lite, and exact-identity GLM.  The
separate user-managed Qwen3-30B-A3B download is
`EXCLUDED_BY_USER_CURRENT_CAMPAIGN` and is neither inspected nor counted.

Current Recovery-V3 local runtime source checkpoint:
`c24ae81b258c5ead3f2f783106ba3e75210f4722`.  This commit adds the
deterministic post-zero static-target selector without widening or rewriting
the prior target.  It fail-closes
generic non-S0 qualification unless it is explicitly requested with an
immutable non-S0 binding.  The GPU runtime workspace that produced the
retained baseline/G1 evidence was
`44981e72c39b317529ee98995dfd478283830623`; a later formal run will bind its
actual runtime source explicitly rather than inferring it from this
publication checkpoint.
The local bulk root is `/root/share/c16_recovery_v3`; recovery payloads are
not staged in `/workspace` or the constrained root filesystem.

### Qwen2.5-7B raw S1 Prefill direct-memory discriminator closeout

The two authorized, non-scientific direct-memory discriminators have now
closed with complete remote-to-local tree SHA equality. Both used the same
exact, live CUTLASS Prefill function, immutable S1/CODE input, `bfloat16`,
`sdpa`, and checksum-stable runtime. The original direct GLOBAL load
(`LDG.E.64`, NVBit static index 29) and the independently selected direct
GLOBAL store (`STG.E.STRONG.GPU`, NVBit static index 3033) each proved 56 exact
function launches and 56 direct callback invocations, yet each emitted zero
address-bearing records. The V2 selector is not a widened V1 filter: it was
selected from the hash-closed NVBit-native map after the V1 zero result.

This precise, phase-target result is
`QWEN7_RAW_S1_PREFILL_DIRECT_MEMORY_CAPABILITY_LIMITED_TWO_EXACT_TARGETS_ZERO`.
It is neither a timing result nor proof that Decode or the model has no memory
traffic. It forbids blind static-index scanning, target substitution,
kernel-name matching, shape/dtype/backend change, or CPU offload. The compact
publication is
[`R5_QWEN2P5_7B_RAW_S1_PREFILL_DIRECT_MEMORY_CLOSEOUT.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_full_authority_recovery_v3/R5_QWEN2P5_7B_RAW_S1_PREFILL_DIRECT_MEMORY_CLOSEOUT.json).
Both raw diagnostic trees remain exclusively under
`/root/share/c16_recovery_v3`; their independent transfer receipts prove
`REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`. Independent Recovery-V3 rows may
continue without treating this Prefill-only target-path limitation as a
campaign-wide blocker.

The authoritative V9 source inventory is now
`/root/share/c16_recovery_v3/receipts/ASSET_CONSOLIDATION_RECEIPT_V3.json`
(SHA256 `e616de31b1a6ea54dcf7a20452331bf2cc50b91dba49a2d112d5523425f7c886`).
It records only non-destructive source use: Llama P0 is source-to-destination
file-count/bytes/SHA-closed under the bulk root; Qwen0.5 and Qwen3-8B are
already hash-closed under that root; Qwen7 raw and AWQ are independently
source-to-destination SHA-closed.  The user-managed Qwen3-30B-A3B path was
not inspected and remains excluded.  DeepSeek's local C16 candidate is only
metadata/tokenizer material, not a complete model; its exact runtime-input
closure remains required.  GLM remains identity-unresolved rather than being
guessed from an unrelated local cache ref.

Asset consolidation V4 supersedes V3 for DeepSeek: the complete exact
`deepseek-ai/DeepSeek-V2-Lite@604d5664dddd88a0433dbae533b7fe9472482de0`
source was non-destructively copied into the bulk root and independently
source/destination SHA-closed across 15 payloads / 31,418,838,087 bytes.
Its V4 inventory row is `EXISTING_ASSET_CONSOLIDATED`; the retained source was
not deleted.  The V4 JSON SHA256 is
`9fd97183fe94c2223ce7bdf67bed5278287096a2522c5b82803b852e47874f7a`.
Qwen3-30B-A3B remains uninspected and
`EXCLUDED_BY_USER_CURRENT_CAMPAIGN`; GLM remains identity-unresolved.

The Llama asset receipt is
`/root/share/c16_recovery_v3/receipts/R1_LLAMA3P2_1B_ASSET_RECEIPT.json`
(SHA256 `7694c95442cc7ff1d3fc8ed1104d5c0d6a50c3a17f779f402ef90669edeb7b47`):
all six model/tokenizer/config payloads total 2,480,783,094 bytes and match
the retained P0 source receipt.  This changes storage/provenance only.  It
does not reopen the separate immutable legacy NVBit ledger: Llama's six
historical NVBit windows remain consumed, so no new Llama G3 capture is
authorized through that ledger.

- Qwen2.5-0.5B-Instruct at
  `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`
  is local hash-closed, its immutable P1 input contract is hash-closed, and
  the seven model payloads are remote-to-local dual-endpoint SHA-closed.
  The transfer receipt is
  `/root/share/c16_recovery_v3/receipts/R2_QWEN2P5_0P5B_DUAL_ENDPOINT_TRANSFER_RECEIPT.json`
  (SHA256 `b69ae26b6de4bf81bd8e15fb1601ffbc52d3d1bd8d3e163ec5d329244bbe77f8`).
- Its non-model R2 runtime preflight passed with `CAPTURE_ALLOWED=YES`,
  RTX3090/SM86, driver 570.124.04, CUDA 12.4, PyTorch 2.5.1+cu124, NVBit
  1.7.5, EAGER loading, child `nvdisasm`, zero stale GPU compute processes,
  and no `MEASUREMENT_ACTIVE` marker.  It did not load a model or emit trace.
  Preflight SHA256:
  `c2e859b0a13ad807a9c5163590a12cc6793124fd85039fe2f4d64ff8d7e8029e`.
- The exact S0/TEXT/B1/T128/Decode4 frozen binding is materialized on the
  GPU host with a package-root symlink to the independently closed model;
  no model bytes were duplicated.  The returned binding SHA256 is
  `bc5c8bb7fc019654b995a471f6f25045fca07ccfa355f0ffdeb0e189959454d5` and
  the returned frozen token list SHA256 is
  `5ec815bc65ee841e1eb41736c74bc8c2b3bcc44edaec730b16e1c7f406a59b30`.
- All Qwen0 frozen runtime bindings are now materialized from existing P1
  receipts and locally SHA-closed: S0/TEXT, S1/CODE, S2/TEXT+CODE+STRUCTURED,
  S3/TEXT, and S4/STRUCTURED.  The seven binding hashes and 14 returned
  compact files are indexed in
  [`R2_QWEN2P5_0P5B_ALL_SCENARIO_BINDINGS_RECEIPT.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_full_authority_recovery_v3/R2_QWEN2P5_0P5B_ALL_SCENARIO_BINDINGS_RECEIPT.json).
  This remains preparation-only and used no GPU model work.
- Qwen2.5-7B raw at immutable revision
  `a09a35458c702b33eeacc393d103063234e8bc28` is now remote-to-local
  dual-endpoint SHA-closed and its 62-payload immutable P2 package verifier
  passed.  Its S0/TEXT/B1/T128/Decode4 frozen binding was derived solely from
  the A@`168c97148ef2bbfaf9bbe199414b0e7a5fc3ed1d` receipt: token receipt
  SHA256 `47686a0239b496ad096cb25fa326e081d9fbadb2b589b6116e4a852dd50f4ffe`,
  derived token list SHA256
  `5ec815bc65ee841e1eb41736c74bc8c2b3bcc44edaec730b16e1c7f406a59b30`, and
  binding SHA256 `a539709d3bfe7a5c051f6e91e89b6bbf1ff877e70fb61aefed8f2ad5f5882f21`.
  The compact consumer receipt is
  [`R2_QWEN2P5_7B_RAW_PACKAGE_BINDING_RECEIPT.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_full_authority_recovery_v3/R2_QWEN2P5_7B_RAW_PACKAGE_BINDING_RECEIPT.json).
  This is an R2 provenance closure only: no Qwen7 raw model execution,
  baseline, census, target selection, or trace was run.
- Qwen3-8B exact-revision payloads are fully hash-closed under `/root/share`.
  It remains outside every measurement window until its separate C16 runtime
  input and resource-admission contracts are closed.

The next authorized GPU work is Qwen0.5 R3 after this compact R2 publication
and a fresh formal-window preflight.  Qwen7 raw remains at R2 until its own
runtime preflight/resource admission passes.  No Qwen3-30B-A3B, model
baseline, census, or trace was started by the preceding R2 checkpoint.

### Qwen0 Recovery-V3 R3/G1 milestone

Qwen2.5-0.5B S0/TEXT has now completed a fresh unprofiled native baseline and
an independently validated G1 lightweight nsys census under runtime source
`a5f1d51247fded1d8e96abc67a98b9f3556f9e7e`.  The profile was kept separate
from baseline timing.  Its `.nsys-rep` (5,072,640 bytes) and SQLite export
(13,729,792 bytes) are retained only under `/root/share/c16_recovery_v3` and
each passed remote-to-local SHA equality.  The catalog has 21,180 phase-linked
kernel-launch rows; operator/layer remains conservatively `UNKNOWN`.

The local control host's nsys 2022.4.2 cannot export a 2024.1.1 report, so the
first bounded SQLite export used the remote 2024.1.1 tool after measurement
ended, then immediately returned it hash-closed; no large TSV was produced.
The compact source/receipt/raw index is
[`R3_QWEN2P5_0P5B_S0_NATIVE_G1_RECEIPT.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_full_authority_recovery_v3/R3_QWEN2P5_0P5B_S0_NATIVE_G1_RECEIPT.json).
Two pre-census nsys setup attempts remain in the budget ledger as
`NON_SCIENTIFIC` failures and are not included in the baseline or catalog.

R4 is now frozen as `RECOVERY_V3_QWEN0_S0_G1_V1` (plan SHA256
`96702cc3608c56c64e3b3ac1d81d28b241f8b10aa20a998f5adb911706702cb3`).
It carries separate Prefill and Decode structural candidates selected solely
by aggregate phase duration.  Both rows retain
`PENDING_R5_NVBIT_NATIVE_MAP`: their nsys names/geometry are only second-pass
keys, never a substitute for an exact live NVBit function identity or static
instruction range.

### Recovery-V3 R5 Qwen0 closeout and V9 asset correction

The current R5 publication is
[`r5_qwen0_budget_closeout`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_full_authority_recovery_v3/r5_qwen0_budget_closeout/)
at artifact checkpoint `4d16bafc41412039a0a60a9bd481dcfc408498c2`.
Its manifest SHA256 is
`ac5c749d9a6473720d52446a4b0ff6aeb2462b063baecf658e3971761d659ca7`.
The implementation anchor is `2c951d8c71fe7e0271332d1d2a724951c42a92d0`;
the runtime code that produced the retained Qwen0 evidence remains
`44981e72c39b317529ee98995dfd478283830623`.

Qwen0 S0 now has direct NVBit identity bindings and independent direct GLOBAL
memory-static targets for both PREFILL and DECODE.  The retained old-tracer
run `8c93675b-bd5c-497f-9371-a7bbd5e1a3d2` is explicitly a
`NON_SCIENTIFIC_DIAGNOSTIC`, not a trace result: its old binary predated the
exact-root/static-index ROI contract.  Its 1,016 retained payloads are
remote-to-local SHA-closed through the independent manifest.  The corrected
tracer binary is provenance-checked but **not executed**.  The fixed ledger
SHA256 `2d2d1cb6da7b09547d7689f7910656038d4f52aaf4f5c041c16f563b479340e1`
proves all six permitted Qwen0 NVBit windows are already consumed.  Therefore
the only valid current outcome is
`QWEN0_S0_G3_CAPABILITY_LIMITED_BUDGET_EXHAUSTED`; no budget reset, target or
range substitution, new raw, or scientific capture claim is permitted.

V9 asset consolidation V2 is stored outside Git under
`/root/share/c16_recovery_v3/receipts/ASSET_CONSOLIDATION_RECEIPT_V2.json`
(SHA256 `3a175867fe8bd7c5a72a1db905dda32e11f178ba1b94e34ce1959356b4d4f116`).
Qwen3-8B is now `ALREADY_UNDER_BULK_ROOT` with full payload size/SHA closure.
The separate Qwen3-30B-A3B user-managed tree remains
`EXCLUDED_BY_USER_CURRENT_CAMPAIGN`: it was not inspected, moved, validated,
or counted.  The retained exact P0 Llama source was copied non-destructively
into the fixed bulk root and is now registered only after destination
file-count/bytes/SHA closure completed.

Qwen2.5-7B raw now also has the six non-S0 immutable frozen bindings
materialized and remote-to-local SHA-closed: S1/CODE, S2/TEXT, S2/CODE,
S2/STRUCTURED, S3/TEXT, and S4/STRUCTURED.  The compact local receipt is
`/root/share/c16_recovery_v3/receipts/R2_QWEN2P5_7B_RAW_ALL_SCENARIO_BINDINGS_RECEIPT.json`
(SHA256 `e3313161185d8fd109533058248224337099a65a0e3beb7ffa4b87fac9dfc29a`)
and the V2 remote/local payload manifest SHA256 is
`867bbe043d71c40a7af818579830cd257306fbd9d4783455e39a53f1f69af8fd`.
The first checksum-manifest attempt was retained as a non-scientific setup
diagnostic because it self-referenced; V2 excludes manifests and verifies all
12 binding/token payloads.  No model was loaded, no GPU was used, and no
measurement marker was armed.  Its next gate is a separate runtime/resource
admission after the ongoing bulk-root asset copy has finished.

Qwen2.5-7B-AWQ P3 non-model inputs are also locally materialized from the
fixed A@`168c97148ef2bbfaf9bbe199414b0e7a5fc3ed1d` package authority and its
manifest SHA256 `704dc320a131e31a6d9fd11a8ac623318777c832b0b699241c5bf3f1c8beda1c`.
The 49 input/receipt payloads are SHA-closed at
`/root/share/c16_recovery_v3/receipts/R2_QWEN2P5_7B_AWQ_MODEL_INPUT_RECEIPT.json`
(SHA256 `7e7280815a2a3203d6e9f4cdad0e8e198a5c4efddf15ab78e109fb8f5d2a3c8b`).
The 5.2-GiB exact AWQ model remains singly stored under the bulk root; no
weights were duplicated or transferred to the GPU node, and no model/GPU
operation occurred.  Remote transfer and resource admission remain separate
future gates.

### Qwen2.5-7B raw Recovery-V3 S1 native/G1 milestone

The prior R2-only statement for raw Qwen7 is superseded for the exact
`S1/CODE/B1/T256/Decode16` binding only.  R2 runtime preflight now passes
with `CAPTURE_ALLOWED=YES` (receipt
`/root/share/c16_recovery_v3/receipts/R2_QWEN2P5_7B_RAW_RUNTIME_PREFLIGHT.json`,
SHA256 `55c270814161f9de9f5234439e0663377582d1d6f49af7c90a0404246273d464).
The node is the fixed RTX3090/SM86, driver 570.124.04, CUDA 12.4,
PyTorch 2.5.1+cu124, NVBit 1.7.5, EAGER runtime profile; no stale GPU process
or measurement marker was present.

The fresh, unprofiled baseline completed under runtime source
`44981e72c39b317529ee98995dfd478283830623`: all parameters and inputs were
CUDA-resident, raw `bfloat16`, `TRANSFORMERS_CONFIG:sdpa`, no CPU offload,
and the three retained checksum-stable measures had median 407.462449 ms.
The first nsys invocation using `--capture-range=nvtx` is retained in the
ledger as `NSYS_FAILED_EMPTY_PROFILE`: that runner's NVTX push/pop ranges did
not arm Nsight's capture-range mode, so it emitted no report and is not a
census result.  The independently identified replacement run used the same
frozen binding with default nsys tracing and retained the NVTX phase ranges
for offline phase attribution.  Its nonempty report is 14,550,782 bytes,
remote/local SHA256
`24d6c5401a3f6fbdb754811d2dc5e4d392545ea73acfe8d9fc662f979f889af6`, and
is closed at
`/root/share/c16_recovery_v3/raw/qwen2p5_7b_raw/S1_CODE/nsys_census_full/S1_CENSUS.nsys-rep`.
The immutable remote artifact manifest is SHA256
`7cbcbc500222e78c03c18ff7d5c39fea56f67ec02fabe1a9d2156e67d97be1ac`; its
dual-endpoint transfer receipt is SHA256
`a7adfc5decc530cc53bb20292f9eb652fd46ca0b1a6a300071c7ee72cbaf98c1`.
There is no remote-only required G1 artifact for this row.

### Qwen2.5-7B raw Recovery-V3 S1 R4/R5 Prefill milestone

Local postprocess closed the complete 97,720-row census without dropping the
kernel population.  R4 froze exactly two phase rows in
`RECOVERY_V3_QWEN2P5_7B_RAW_S1_G1_V1` (target-plan SHA256
`6c38f45569413d2a4fa65b743e925ec9a28fc703537d65dd64642932ea0a2b35`): the
Prefill structural ordinal is 46 and Decode structural ordinal is 1218.  The
names and geometry are provenance keys only; they are not a target-selection
substitute.

R5 then ran one non-scientific direct NVBit launch inventory under runtime
source `1f1b0692c6a894f842d9e095b237415315e4172d`.  The retained 12,809,379
byte inventory is remote/local SHA-closed at
`/root/share/c16_recovery_v3/raw/qwen2p5_7b_raw/S1_CODE/r5_launch_inventory/launch_inventory.tsv`
(SHA256 `51e75050727c6789966037f77154a997b6f773676aa2cf706163364c66e0c40c`).
Its direct-function binding receipt SHA256 is
`ec7abbddfbc4c0adb71dd05715fb4e517eefe985efea69692a3d58764333af2e` and
binds the Prefill CUTLASS function and Decode BF16 GEMM function through
exact loaded NVBit identities plus the frozen grid/block provenance.  It
does not use a kernel-name-only match and it emitted no trace.

The Prefill exact function subsequently completed an NVBit-native static map
with 5,288 instructions.  The map is remote/local SHA-closed at
`/root/share/c16_recovery_v3/raw/qwen2p5_7b_raw/S1_CODE/r5_static_map_prefill/PREFILL_STATIC_MAP.tsv`
(SHA256 `437e31c9a76d65ebce1eaa8dd8b802bd836f367befdf87417c3eb92d15eec125`).
The direct target receipt SHA256
`116c3ea2997ced9ca1469688789f85ba40de5e08f1e655f9988840ca9118171c`
selects `LDG.E.64`, GLOBAL, NVBit static index 29, vector ordinal 29, and
offset 464.  This is direct `nvbit_get_instrs` evidence: neither historical
ordinal 348 nor SASS text-line 34 was used.  The map-only diagnostic has no
instruction insertion, no memory trace, and is not timing/scientific data.

Decode now has its own exact NVBit-native static map: 704 instructions,
map SHA256 `3d9e6e70e0c2d6e583a62b5de4670439b664cc7fffe8d4a85a9cdeecef5108a7`,
and direct target receipt SHA256
`17fb1ae199c800f5eef5954a27f49a31f4a9e7c50d56b73bb0f2ef02c27eb9d6`.
It selects GLOBAL `LDG.E.LTC128B.CONSTANT`, NVBit static index 45, vector
ordinal 45, and offset 720. This is independent direct `nvbit_get_instrs`
evidence and is not a reuse of Prefill's index 29. Both phase maps retained
the identical frozen output checksum/backend and were map-only diagnostics,
with no instruction insertion or trace payload.

Two failed Decode-map configuration attempts are retained rather than erased:
the first omitted the tool-required `C16_NVBIT_CODE_OBJECT_SHA256` and ended
in the tool's pre-forward abort; its stale active-measurement marker was moved
intact into the run only after the recorded PID was absent, then its zero-byte
failure was reconciled through a single exclusive legacy ledger lease. The
next attempt used a nonexistent adapter name and was normally ledgered as a
zero-byte `MODEL_NVBIT_QUALIFICATION_FAILURE`. Their closeout receipt SHA256
is `e0f5589d327a7cfcd3181961c1e3989e163a4423bdf1920f0558d76b5eff63d6`;
`MEASUREMENT_ACTIVE` is absent and no GPU compute process remains.

The raw-Qwen7 legacy diagnostic ledger is now exactly 5/6 NVBit rows, all
retained; it is not reset or bypassed. Formal Recovery-V3 capture is instead
gated through the pre-existing explicitly authorized Recovery ledger, with
the original 70-entry legacy snapshot SHA256
`7a109337471d98fe50d1be353995b398b3ebee0a8e0504a692843f04736f248d` and
the current 87-entry live ledger proven append-only. The code path enforcing
that bridge is runtime source `1fc4b44c29df7842d22c66902c34ef0e9c3d1057`.
No formal R6 capture has started: it remains conditional on the two closed
phase targets, formal storage/prewarm gates, and a parent-owned Recovery
lease.

## Final post-Llama multi-model dataset publication

The authoritative compact publication is
[`lane_g_retry570_nvbit175_post_llama_multimodel_dataset`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvbit175_post_llama_multimodel_dataset/).
Its manifest SHA256 is
`9b202d9dbf88816d24ec85332038e5e9df6e64b44e11aba304855d9b4ee80f51`.
The publisher implementation anchor is `9bef6df1770b13cd3c6fb28dd71018a284244371`;
the following handoff commit is publication provenance, not a change to its
producer logic.

Llama remains the accepted reference dataset from
`2e955e007bcabcd3ec24a5f9d24768d27caaee27`, with source manifest
`0d8aeb74729a06e2188359cca2eb18c3884ea5b108723d6966778a161c4aaacc`.
It has retained, remote-to-local SHA-closed target memory traces totaling
16,319,706 bytes. `LARGE_INDEX_PREFILL_TARGET` and the independently mapped
`DECODE_INDEX_TARGET` remain distinct; the LargeIndex decode zero is
`STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED`, not a claim of no decode memory access.

Phase A recovered exact immutable identities for Qwen-0.5 and Qwen-7B-AWQ,
but no matching local assets existed and the same-session authorized upstream
route was `NETWORK_UNREACHABLE`; both are
`BLOCKED_ASSET_UNAVAILABLE_AFTER_AUTHORITATIVE_SEARCH`, not substituted
captures. DeepSeek and GLM are each
`BLOCKED_IDENTITY_UNRESOLVED_REQUIRES_USER`: the retained C15 static candidate
is not a C16 runnable identity, and generic `GLM` is not an exact model
identity. No Qwen, DeepSeek, or GLM model run or trace was emitted.

`DOWNSTREAM_CONSUMER_VALIDATION.json` validates the C16 requirement as
`PHASE_TARGETED_MEMORY`; the unrelated M4 `kernelslist.g`/Accel-Sim path is
explicitly excluded. The final remote quiescence audit reports
`ACTIVE_GPU_PROCESS_COUNT=0`, `ACTIVE_DIAGNOSTIC_PROCESS_COUNT=0`,
`MEASUREMENT_ACTIVE=false`, and `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`.

Historical recovery-v2 checkpoint: `C16_NVBIT175_MULTIMODEL_RECOVERY_V2_LLAMA_COMPLETE_NEXT_MODEL_INVENTORY`.

## Active recovery-v2 checkpoint — Llama complete

The prior `COMPLETE_WITH_BLOCKED_MODELS` campaign is preserved below as
historical closeout; it is superseded for the new recovery-v2 namespace, not
rewritten. The new consumable Llama S0--S6 pack is
[`lane_g_retry570_nvbit175_recovery_v2/llama_3p2_1b`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvbit175_recovery_v2/llama_3p2_1b/).
Its manifest SHA256 is
`0d8aeb74729a06e2188359cca2eb18c3884ea5b108723d6966778a161c4aaacc`;
the publication producer implementation anchor is
`01d688227d828468421d6eb4d12f89808206027c`.

`LARGE_INDEX_PREFILL_TARGET` remains the exact full-mangled Llama
`indexSelectLargeIndex`, NVBit static `[101,102)`, `LDG.E.U16`, with static
text-line 34 forbidden and historical candidate 348 not reused. It has 8,192
address-bearing records in each S3/S4 prefill capture and in S5 Prefill.
Its zero counts through logical Decode1--4 are explicitly
`STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED`: the exact LargeIndex function is absent
from the decode kernel census, not evidence that decode lacks memory access.

The bounded no-NVBit decode census directly found the same shape-dependent
`indexSelectSmallIndex` dispatch in every actual cache-correct decode forward
(logical Decode2--4; Decode1 is the frozen prefill-derived greedy token and
has no separate CUDA forward). A separate NVBit 1.7.5 native map selected
`DECODE_INDEX_TARGET` static `[17,18)`, `LDG.E`; the complete-decode capture
then recorded 64 address-bearing rows in each of Decode2, Decode3, and
Decode4 with the frozen output checksum unchanged. The six retained raw
traces are remote-to-local SHA closed and remain outside Git. The immutable
legacy ledger still hashes to
`7a109337471d98fe50d1be353995b398b3ebee0a8e0504a692843f04736f248d`;
recovery-v2 used its independent eight-window namespace and did not rewrite
the historical rows.

Next queued work is metadata-only exact identity/asset recovery for Qwen-0.5,
Qwen-7B-AWQ, DeepSeek, and GLM. No model variant will be guessed or
substituted; a model whose exact identity/asset cannot be recovered will get a
separate `BLOCKED_ASSET_UNAVAILABLE` receipt while the next model continues.

## Final NVBit 1.7.5 multi-model campaign closeout

The final compact campaign pack is
[`lane_g_retry570_nvbit175_full_multimodel_campaign`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvbit175_full_multimodel_campaign/).
Its `PUBLISH_MANIFEST.json` is hash-closed and its validator checks every
published payload for existence, size, SHA256, and duplicate paths. Raw traces
are not committed.

Llama completed C0 identity freeze, S1 full frozen S0/B1/T128/decode4
no-trace runtime evidence, and S2 direct NVBit 1.7.5 requalification. Its
exact target is the full mangled `indexSelectLargeIndex` function and direct
GLOBAL `LDG.E.U16` static range `[101,102)`; historical SASS text-line `34`
is explicitly excluded, and historical candidate `348` is not reused. S3 did
not launch: before any model/GPU process or `MEASUREMENT_ACTIVE`, the immutable
remote ledger proved that all six allowed `NVBIT` windows for
`c16_llama32_1b_frozen_compatible` had already been consumed by retained
historical diagnostics. The campaign preserves those six rows unchanged and
does not reset, reclassify, or bypass the hard deployment budget. Llama is
therefore `BLOCKED_RUNTIME_WITH_FROZEN_CONTRACT`; no new Llama raw trace was
created.

The C0 asset inventory proves Qwen 0.5, Qwen 7B-AWQ, DeepSeek, and GLM lack a
local exact config/model asset on this node. Each is
`BLOCKED_ASSET_UNAVAILABLE`; no network download, substitution, model run, or
trace was attempted. The remote ledger copied for closeout is locally SHA
closed, and the final remote check found zero active GPU processes and no
`MEASUREMENT_ACTIVE` marker. This is a campaign closeout with explicit
blockers, not a claim of missing model traces.

## NVBit 1.7.5 Q0/Q1/Q2 capture qualification — stop for review

The new compact, non-scientific capture-qualification publication is
[`lane_g_retry570_nvbit175_capture_qualification`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvbit175_capture_qualification/),
with `PUBLISH_MANIFEST.json` SHA256
`f60b57cfc1ef172bd8c66ac16c7fede9208b530745f0948e6693095f6306d196`.
The actual Q1 runtime/capture code anchor is
`8440c04512ef372480aa71a077bacfa7e55e8eb2`; the distinct publication validator
anchor is `31be238c49a4a31c19e8cb238655877ba8e5ee2e`.

The frozen known-good profile remains RTX3090/SM86, driver `570.124.04`, CUDA
12.4 (`nvcc 12.4.131`, `nvdisasm 12.4.127`), PyTorch `2.5.1+cu124`, exact
`libtorch_cuda.so` SHA256
`761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`,
NVBit 1.7.5, and `CUDA_MODULE_LOADING=EAGER`. The machine-readable profile
and diagnostics-only preflight remain at
[`NVBIT_LANE_G_RTX3090_CUDA124_KNOWN_GOOD.json`](../../../runtime_profiles/NVBIT_LANE_G_RTX3090_CUDA124_KNOWN_GOOD.json)
and `retry570_nvbit175_preflight.py`; the preflight receipt is
`CAPTURE_ALLOWED=YES` and its SHA256 is
`c2e859b0a13ad807a9c5163590a12cc6793124fd85039fe2f4d64ff8d7e8029e`.

Q0 prewarm/runtime readiness passed with the original Lane G tracer and no
matching dynamic range: `LANE_G_RUNTIME_READY`, output checksum
`8c62c08fcc833f223182df024f4ed698c8e3fc93daf8e259c14d35e8899e665c`, and
`PREWARM_TRACE_COUNT=0`. It directly froze kernel id 6 and the full mangled
`indexSelectLargeIndex` identity. Two independent Q1 processes then armed
`MEASUREMENT_ACTIVE` only after READY, each captured exactly that kernel, and
each produced one 481,651-byte trace with 7,360 parseable records and 192
address-bearing `LDG.E` records. Q1 target/remote walls were
`6.890535 / 7.027329` and `6.775636 / 6.878313` seconds; local SSH wall was
observed at approximately `7.5 / 7.4` seconds respectively. Both raw trees
are remote-to-local SHA closed, no GPU process remains, and the marker is
absent after cleanup.

Q2 validates required schema/version headers, exact function/kernel binding,
instruction rows, address-bearing memory records, and a final-newline
truncation guard. The trace format does not provide record timestamps or a
global sequence field, so the publication correctly uses the parent-controlled
zero-before-arm and ordered READY/CAPTURE lifecycle proof rather than claiming
per-record timestamp ordering. This is `NOT_NATIVE_TIMING` and
`NOT_SCIENTIFIC_CAPTURE`; it authorizes nothing further. Stop for user/ChatGPT
review before any Llama/Qwen/full-model/C-target activity.

## Current NVBit engineering-unblock qualification

The compact publication is
[`lane_g_retry570_engineering_unblock`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_engineering_unblock/),
with `PUBLISH_MANIFEST.json` SHA256
`9b343570d58b060eec4009d20ea81f638081c3001e88220079c91cca365b8f87`.
The publication-generator implementation anchor is
`7f3a7a9861e816751cd388003ac00b5e8a62af3e`; the final publication/handoff
commit is distinct and reported after this checkpoint is committed.

The one authorized NVBit 1.8 EMPTY+EAGER first-use qualification did not reach
`READY` within its 60-second target cap. Its target/remote/local walls were
`60.660996 / 60.755267 / 61.171210` seconds. It stopped during first GPU input
preparation, so `process_to_ready_s`, `round1_s`, and `round2_s` do not exist;
one-time versus repeated behavior is not determined for NVBit 1.8. The attempt
remains in the budget ledger as `NON_SCIENTIFIC_DIAGNOSTIC`. Runtime source
`9a12ff1aec0410f6795b68c7df1710c3d5610fec` produced the window; later commit
`f56b33e501366b01ffc7d60252de8ce2044202c7` only corrected the invalid ledger
classification spelling and did not rerun it.

The version differential held the RTX3090, driver `570.124.04`, CUDA 12.4,
PyTorch `2.5.1+cu124`, `libtorch_cuda.so`, and tiny workload fixed. NVBit 1.7.5
passed official `instr_count_bb + vectoradd`, then completed the EMPTY exact
reproducer in `5.677317` seconds. Although the harness requested LAZY, NVBit
1.7.5 reported and the CUDA API confirmed EAGER; this vendor behavior is
preserved as a caveat. The independent NVBit 1.8 EAGER result still failed to
reach READY, so the classification is `NVBIT_VERSION_SENSITIVE_CORE_PATH`.

Finally, the normal Lane G C16 tracer rebuilt against exact NVBit 1.7.5
completed one EAGER C2 tensor-fill first-kernel smoke. Submission/completion
were `5.630197 / 5.872201` seconds; target/remote/local walls were
`6.655896 / 6.759123 / 7.177605` seconds. A no-match range kept tracing
inactive and an independent scan found zero `.trace`/`.trace.xz` files.

The recommended unblock is therefore to pin NVBit 1.7.5 archive/core/tool
hashes, perform a bounded EAGER zero-trace prewarm outside
`MEASUREMENT_ACTIVE`, emit `READY` only after identity, terminal, zero-trace,
and process-cleanup checks, and create the formal measurement gate afterward.
This is engineering qualification only: no model, Llama, Qwen, C target,
trace, scientific capture, 300-second watch, or 6+6 rerun was performed or is
newly authorized. All 25 retained diagnostic payloads plus the final ledger
are locally SHA-closed; `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`,
`ACTIVE_GPU_PROCESS_COUNT=0`, and `ACTIVE_DIAGNOSTIC_PROCESS_COUNT=0`.

## Current NVBit callback-bookkeeping root cause

The current compact publication is
[`lane_g_retry570_callback_bookkeeping_root_cause`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_callback_bookkeeping_root_cause/),
with `PUBLISH_MANIFEST.json` SHA256
`8886a28deb2c6353f88ea393064a480e8a29c0541c691f1e2e1cd2aa725fe8cb`.
Its diagnostic runtime producer is
`e27ce12addcea5b9da27b4fa02f0f6e6a462be09`; the governing read-only root-cause
handoff is `43c50becb8b3bc41673f77f5674bf15308954440`.

`RAW = HANG`; `EMPTY = HANG`. The true RAW callback retained only a fixed,
preallocated POD ring: 196 events, zero drops, maximum callback depth one,
zero reentrancy, and a final `cuLibraryGetModule` entry decoded offline.
The EMPTY callback contains only `return;`. Its bounded GDB snapshot is
`std::_Hash_bytes -> elfModuleHashMap::operator[] -> Nvbit::module_loaded ->
nvbitToolsCallbackFunc`. Ownership is therefore NVBit 1.8 precompiled core,
not the RAW census and not the Lane G targeted-memory tool. The vendor archive
is `core/libnvbit.a` SHA256
`db221829106673bcd69d1e05766136f80e2df4497fb8415d8c2f298b96c302f7`;
`Nvbit::module_loaded` is in `nvbit_imp.o` and `elfModuleHashMap` in
`tools_shared_readelf_caches.o`. It provides no DWARF source line, so no
private-STL layout or invented FILE:LINE is claimed.

Per-run wall accounting is explicit: TRUE RAW target/remote/local wall is
`25.302602 / 25.416366 / 27.138402` seconds; EMPTY is
`25.317044 / 25.423447 / 25.933204` seconds. Both use a 25-second externally
supervised target child process group, 32-second remote transaction cap, and
40-second local SSH cap; both received TERM and exited in the two-second grace
without KILL. All retained diagnostic payloads are locally SHA-closed,
`REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`, and
`ACTIVE_GPU_PROCESS_COUNT=0`.

This confirms the core bookkeeping path, but does **not** establish whether
its first-use cost is finite/one-time or repeated: the exact operation never
returned within the permitted cap, and historical EAGER moved work before the
exact marker without completing under its short cap. `MEASUREMENT_ACTIVE`
prewarm and all formal capture remain unqualified. The historical Llama
scientific state remains
`NVBIT_RETRY570_LLAMA_MODEL_CANARY_INCONCLUSIVE_FILTERING_NOT_DISAMBIGUATED`.
No model/Llama/Qwen, C target, trace, scientific capture, 300-second watch, or
historical 6+6 re-run is authorized by this checkpoint.

## Exact historical-target discovery boundary

The current exact-target closeout is
[`lane_g_retry570_exact_discovery_boundary`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_exact_discovery_boundary/),
with fixed `PUBLISH_MANIFEST.json` SHA256
`4e0113742fa7a4b0fd409822c71e67c584e213f28edfaa967df4065a696c33f2`.
Its status is
`NVBIT_RETRY570_EXACT_TARGET_DISCOVERY_INCONCLUSIVE_PRE_LAUNCH_CALLBACK_BOUNDARY`.
The two actual diagnostic runtime producer commits are distinctly pinned at
`245fac983faf8188044b4ce6926488972fcac0f6` (initial discovery-only tool) and
`845cff8256391e2d8cd0919afc3a3581353ca126` (pre-target-name-lookup boundary
tool); the final publication/handoff commit is reported separately when this
closeout is committed.

Both hash-closed 60-second exact R2_D0_I64_A replays reached
`EXACT_TARGET_SUBMISSION_BEGIN` but never emitted the NVBit target launch
callback. The second replay proved that four preceding CUDA launch-name
lookups completed in at most 1 microsecond each, while the exact target did
not even emit `PRE_TARGET_NAME_LOOKUP_BEGIN`. Its twelve post-submission
snapshots retained a CUDA-attached, CPU-active process (104--156% CPU), 0% GPU
utilization, no `nvdisasm` child, and non-destructive state/wchan/syscall
evidence; node policy denied kernel-stack symbolization. Consequently, this
is a pre-target-callback boundary, **not** evidence for related-function graph
expansion, a pathological function, duplicate `get_instrs`,
`get_related_functions`, or insertion/enable/launch work in that exact target.

The C4 GEMM result (89 related functions, 88 enumerated, 66,032 static
instructions, 19.969523 s cumulative `nvbit_get_instrs`) remains an independent
general reference only; it must not be assigned to this index-select kernel.
No per-function discovery distribution, static-instruction count, duplicate
test, or same-process reuse test exists for the target because its callback was
never entered. The next smallest experiment is not authorized: it would be a
bounded exact-input **no-op** NVBit launch-callback-arrival probe, with no name
lookup, discovery, instrumentation, trace, model, or C target. The Llama state
therefore remains `INCONCLUSIVE`, not NO-GO; no Llama/Qwen, trace, scientific
capture, C target, 300-second watch, or historical 6+6-window rerun was run.
All 38 retained raw payloads have remote-to-local existence/size/SHA closure;
`REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0` and
`ACTIVE_GPU_PROCESS_COUNT=0`.

## Current bounded PyTorch/NVBit first-kernel isolation

The current non-scientific diagnostic checkpoint is
[`lane_g_retry570_pytorch_stage_diagnostic`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_pytorch_stage_diagnostic/),
with fixed `PUBLISH_MANIFEST.json` SHA256
`7b803deecea24e273f3c368081174a27910e7bfd94f503232c8e61cd4129a553`.
Its status is `NVBIT_PYTORCH_FIRST_KERNEL_STAGE_DIAGNOSTIC_COMPLETE`; its
runtime producer source is
`982135c3a7d946f4d4be8705239d4b332802330b` and the diagnostic-only NVBit
timing-probe tool is hash-closed at
`07ba183f1f27f231af249ad6f2329a70b84d3de75e0bff8974696e5b8c59b845`.

It ran C0 CUDA initialization, C1 allocation, C2 tensor fill, C3 elementwise
add, and C4 small GEMM as ten independent native/NVBit processes. All completed
under their fixed 60-second limits, produced no trace, and are not scientific
timing or C-target evidence. C2/C3 had one related function and about 0.23 s
of `nvbit_get_instrs()` discovery. C4's first CUTLASS GEMM launch expanded to
89 related functions (88 enumerated), 66,032 total static instructions and
19.969523 s of instruction discovery; insertion/enable/synchronization then
completed, with the full C4 probe ending at 20.041227 s and child completion
at 23.064094 s. The retained five-second snapshots show advancing discovery
markers and `do_wait`/futex wait states, not a fixed mutex deadlock; node policy
denied symbolized `/proc/.../stack` reads.

This localizes the minimal-PyTorch boundary to related-function/static-
instruction discovery expansion (B), rather than establishing A, C, or D. It
does not reopen the already-closed 300-second watch and does not authorize
Llama, Qwen, a trace, or any C frozen target. A separately authorized future
longer diagnostic could be technically useful only with an exact bounded
function/related-function scope. All 75 retained payloads (772,515 bytes) have
remote-to-local size/SHA closure, tree SHA256
`d411d972d08fe9d5f255e2dec84251cfd74c9a70da6bb29faa90f7ea5b73aaaa`;
`REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0` and `ACTIVE_GPU_PROCESS_COUNT=0`.

## NVBit nvdisasm path-repair gate

The new closeout is
[`retry570_nvdisasm_path_repair`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvdisasm_path_repair/),
with fixed `PUBLISH_MANIFEST.json` SHA256
`c9b4daf8a2f8bd2a8c54d2ddd27c3ec2ed6ca625c3c8d2393436e9aec2665f59`.
Its result is
`NVBIT_NVDISASM_PATH_CONTRACT_FIXED_RUNTIME_SMOKE_NOT_QUALIFIED`.

This was a harness configuration defect, not a missing CUDA component:
`/usr/local/cuda-12.4/bin/nvdisasm` exists and is version 12.4.127, while
the original child PATH omitted `/usr/local/cuda-12.4/bin`. NVBit 1.8 requires
`nvdisasm` to be discoverable through PATH. The fixed source contract verifies
the absolute path, prefixes that exact directory into every injected child
PATH, records the absolute provenance, and sets `NVDISASM=nvdisasm`; it does
not depend on a transient shell export. The repair source is
`b76fb566144bb7ca4f7c4356337b36bc0fa65903`; the fixed smoke runtime is
`26a24b07f922df259dcc6823d1915c69b6f0f02a`.

Gate A (`nvdisasm --version`) and Gate B (NVBit 1.8 official
`instr_count_bb` plus vectoradd) passed. Gate C, the Lane G PyTorch
first-kernel smoke with the same environment contract and official tool,
passed the old `nvdisasm not found on PATH` boundary and reached
`FIRST_CUDA_KERNEL_SUBMISSION_BEGIN`, but did not complete a first CUDA kernel
or emit the official kernel marker within its fixed 60 seconds. It produced no
trace or scientific data. Its raw historic `EXTREME_STARTUP_OVERHEAD` label is
retained but normalized by `c9b0be4435b31f389d34854a937a6dff2e42eb1d` as a
60-second path-smoke timeout—not a 300-second long-watch diagnosis.

Accordingly, formal long-watch reapplication is **not qualified**. No
long-watch, model, C target, trace, scientific capture, or 6+6-window rerun
is authorized from this checkpoint. The remote has no active GPU process or
measurement marker, and all retained smoke payloads are locally SHA-closed.

## One-shot NVBit long-watch closeout

The retained microreproducer closeout remains valid and its existing 6+6
bounded NVBit windows were not rerun. The new compact checkpoint is
[`retry570_long_watch_diagnostic`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_long_watch_diagnostic/),
whose `PUBLISH_MANIFEST.json` SHA256 is
`e5a2488994a1abd82b1ebb87792ad6b662a28b23aa34fa87547708c19cccac9d`.
The runtime harness actually used is fixed at
`d8021532adfd94b4196785475f5c3914a3f51c2e`; its existing NVBit1.8 map-only
tool remains fixed at source `f08af62e4bb77559617bd14d5df9a13d2e236873`
and SHA256
`ae4e4e632a4afad0d5dda4b7f7aac2b460135784676765350945137a722cb5c0`.

The no-NVBit control completed the same finite index-select microreproducer
and observed first CUDA-kernel completion at `2.820031002163887` seconds.
It was followed by exactly one NVBit map-only long-watch, durably reserved at
300 seconds with 5-second sampling. That process reached
`FIRST_CUDA_KERNEL_SUBMISSION_BEGIN` but ended after about 2.87 seconds,
before a first completed CUDA kernel, because the NVBit-side resolver emitted
`ERROR: /usr/local/cuda-12.4/bin/nvdisasm not found on PATH!!!`. The executable
was independently observed on the node; this evidence establishes only a
tool-startup/path-resolution configuration failure. It did not reach the
300-second discriminator. Accordingly the closeout state is
`NVBIT_LONG_WATCH_DIAGNOSTIC_INCONCLUSIVE_TOOL_STARTUP_CONFIGURATION_FAILURE`:
it does **not** establish either
`NVBIT_PYTORCH_PRE_FIRST_KERNEL_STALL_CONFIRMED` or
`NVBIT_PYTORCH_EXTREME_STARTUP_OVERHEAD`.

The one-shot authorization is closed, so a second long-watch is forbidden.
No trace, static map, model, Qwen, Llama, frozen C target, timing result, or
scientific capture was produced. All small retained payloads and the ledger
are SHA-closed locally; `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0` and
`ACTIVE_GPU_PROCESS_COUNT=0`.

## Current microreproducer closeout

The newest Retry570 checkpoint is
[`retry570_microreproducer_discriminator`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_microreproducer_discriminator/).
Its fixed `PUBLISH_MANIFEST.json` SHA256 is
`87ed9580ebad311a6bd553cd07fec8ed53d462b783d6728aa61815cf8736efb0`.
The publication-generator source commit is
`c1325a324ef94f2b5dcc0399ff507dce86f60c2a`; the actual final NVBit
diagnostic producer is distinctly anchored at
`f08af62e4bb77559617bd14d5df9a13d2e236873`.

It used no full Llama model to discover a static map. A finite exact
`torch.index_select` microreproducer matched the observed RTX3090,
driver `570.124.04`, PyTorch `2.5.1+cu124`, and
`libtorch_cuda.so` SHA256
`761b14acafb8b02011e32d11bd437b63cca3fe882b9c4a02c89fd01d738ccb6a`.
The complete Llama candidate mangled identity was required, never a short
name. Under correct `CUDA_INJECTION64_PATH`, both the optimized mapper and a
final lifecycle-free exact-map tool bounded out before the first micro CUDA
kernel. The latter had no context/tool-init hook, CUDA allocation,
instrumentation, or mapper cache. Consequently neither a static map nor an
authoritative NVBit instruction index exists. This is a narrow
NVBit/PyTorch callback-path limitation for the setup, not a causal driver or
model-incompatibility claim.

Both the P0 Llama deployment and the isolated microreproducer have exactly
six accounted NVBit windows; no additional NVBit diagnostic, Llama, Qwen, C16
tracer, or C frozen-target operation is authorized on this node. The retained
raw/ledger/marker evidence is locally SHA-closed:
`REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`,
`ACTIVE_GPU_PROCESS_COUNT=0`. The state remains `INCONCLUSIVE`, not NO-GO.

The NVBit-native static-index pass is closed in
[`retry570_nvbit_native_static_map`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvbit_native_static_map/).
It does **not** establish an index: `348` remains only
`HISTORICAL_CANDIDATE_ORDINAL`, and `34` only `SASS_TEXT_LINE_COUNTER`.
The direct `nvbit_get_instrs()` map-only Llama S0 run reached model load but
timed out at 180 seconds without forward completion, target-function launch,
or `LLAMA_INDEXSELECT_NVBIT_STATIC_MAP.tsv`. Thus no authoritative NVBit
static index or memory-instruction target exists; exact-memory/C16 tracing,
Qwen, and C frozen targets remain forbidden. This is not a zero-record NO-GO
or a model/NVBit incompatibility claim. All retained diagnostic artifacts are
locally hash-closed and `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0`.

The post-resize node consumed the exact minimal immutable P0/Llama
package subset.  P0 commit
`20fb38e6ca629f1a93db7939248bd1a03790724c` and package manifest SHA256
`ac59f0d2aca95021c686948d7244ce50375530bbe983c8508ca5f6954e80230f`
are closed in [`retry570_p0_llama`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_p0_llama/).
The frozen M1 S0/TEXT binding is exact B1/T128/decode4 and has no tokenizer
execution or context resize. The disambiguation run binds runtime source
commit `48c330fbda219db12146ea96ed2d08230c3e8b08`; its historical producer
code anchor is `c4597507d50d4ebce67ef0efc6ea50dcdea1183c`.

The `48c330fb` no-go package remains a valid historical publication/provenance
checkpoint, but its scientific inference is superseded: its valid official
intervals `[0,1)` and `[0,8)` did not prove that a memory instruction was
covered. The new hash-closed package is
[`retry570_llama_model_disambiguation`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_llama_model_disambiguation/).
It used the identical Llama identity to obtain a real NVTX-contained kernel:
`indexSelectLargeIndex`, nsys grid ID `1`. The required frozen contract is
`LDG.E` at static ordinal `348`, `INSTR_BEGIN=348`, `INSTR_END=351`. An
already-completed historical attempt instead bound `[34,35)` because `34` was
an SM86 SASS-text instruction-line counter. There is no established
equivalence between `34` and the authoritative `348`; that attempt is retained
only as `UNQUALIFIED_ORDINAL_34_ATTEMPT`, not as a test of the frozen contract.
It also timed out at its 180 s guard before proving a target launch, memory
record, or model-forward completion. Therefore this is
`MODEL_NVBIT_QUALIFICATION_DIAGNOSTIC` only, never native timing or a C target
result; it is neither a disambiguated zero-record NO-GO nor a model-NVBit
incompatibility claim. The C16 tracer was not run.

No Qwen0.5, Qwen7-AWQ, or raw-Qwen payload has been transferred, and no C
`SELECTOR_R/B48` frozen target has been read or executed. No target/shape/
context/dtype/backend/offload or kernel-name substitution occurred.
`NVBIT_STORAGE_ESTIMATE.json` remains `NOT_APPLICABLE_NO_REAL_MODEL_TRACE`;
both local receiver mounts remain below the 100 GiB formal-campaign gate.

The new-node observed identity is bound by
[`C16_RETRY570_NODE_IDENTITY_RECEIPT.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570/C16_RETRY570_NODE_IDENTITY_RECEIPT.json).
It is an RTX3090 / SM86 node with actual driver `570.124.04`; this is an
observed receipt, not a marketplace claim.  Following resize/restart, the
remote disk is 200 GiB total with 198,796,951,552 bytes available, passing the
100 GiB formal-capture storage gate.  The new GPU UUID is recorded in the
post-resize receipt.  No C target has been read as an execution choice,
altered, or substituted.

Q1's sole tiny NCU permission canary reached the diagnostic CUDA fixture as
root but returned `ERR_NVGPUCTRPERM`, emitted no counter result and produced no
`.ncu-rep`.  G2 is therefore current-instance capability-limited; it will not
retry metrics, targets, or privilege variants.  See
[`G2_RETRY570_NCU_CAPABILITY_LIMITED_RECEIPT.json`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570/G2_RETRY570_NCU_CAPABILITY_LIMITED_RECEIPT.json).
This does not block Q2 NVBit compatibility qualification.

CPython 3.10.12 was built in an isolated remote prefix from the official source
archive.  After bounded `libbz2-dev` and `libffi-dev` build-dependency repair,
the 66-wheel CP310/cu124 wheelhouse passed no-index resolver dry-run,
installation, `pip check`, and import closure.  The base Python 3.12
environment was not a scientific runtime substitute.  NVBit 1.7.6 archive and
both tools were hash-closed.

The original Q2 closeout correctly recorded that NVBit 1.7.6 `instr_count`
and the C16 tracer timed out at `ELEMENTWISE_PREPARE`; it remains a retained,
non-scientific diagnostic record.  A subsequent bounded V2 discriminator
held all node and PyTorch inputs fixed, then established a narrower boundary:
NVBit 1.7.6 `instr_count_bb` and `mem_trace` also time out before the workload
kernel, while NVBit 1.8 `instr_count_bb`, `instr_count`, and `mem_trace` pass
both elementwise and GEMM.  NVBit 1.8 official `mem_trace` emits real memory
records, and the C16 tracer rebuilt against NVBit 1.8 emits real traces for
both workloads.  The resulting state is
`NVBIT_RETRY570_MEMORY_TRACE_PATH_QUALIFIED`, not a claim about model or C
target compatibility.

No model payload was transferred, and no Llama, Qwen0.5, Qwen7-AWQ, G2
target, or G3 target was launched.  Exactly one post-resize PyTorch
elementwise+C16-NVBit1.8 sanity exited normally and produced nonzero trace;
the complete prior 1.7.6/1.8 matrix was deliberately not repeated.

The full compact evidence and dual-endpoint diagnostic raw closure are in
[`retry570_q2_closeout`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_q2_closeout/).
`REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0` and `ACTIVE_GPU_PROCESS_COUNT=0`.
Its fixed closeout manifest is `PUBLISH_MANIFEST.json`, SHA256
`56aa8adfe81e259ff358d6d06341444136481bf7bfb2ff6e7878c27a48735804`;
the independent payload validation receipt is `PUBLISH_VALIDATION_RECEIPT.json`.
The direct-fixture producer anchor is `d67d2aea7b6e4e17b2e095633700720da13135ce`;
the existing PyTorch workload producer anchor is
`d1a87532ac71de796b48c622743bb1826eb2ecec`.  This closeout publication
commit is deliberately distinct from both runtime-code anchors.

The current discriminator evidence is in
[`lane_g_retry570_nvbit_v2`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_nvbit_v2/).
Its dual-endpoint transfer closure is
`NVBIT_COMPATIBILITY_TRANSFER_RECEIPT.json`; it has no remote-only required
artifact and the node has no active GPU process.  Its fixed publish manifest
SHA256 is `46189eb85b716ba39c73406613d88852d33bda461965d9dc77f02abe904fc8fa`.

The current post-resize checkpoint is
[`lane_g_retry570_post_resize`](../../../review_packs/C16_MULTIMODEL_NATIVE/lane_g_retry570_post_resize/),
manifest SHA256 `c262464c9ee9757905b295bb177d5da6f1ce3ab8b2bb9c4a550e7b9dde0349a2`.
The next permitted stage is M1 Llama model-level NVBit qualification.

The only eventual G2/G3 authority was immutable C commit
`d55075b7752380d6bd22328547db21a5e24eeed2`, `SELECTOR_R/B48`.  Qwen7 raw,
AWQ S3/S4, changed shapes/context/batch/dtype/backend, CPU offload, and
target substitution remain forbidden.
