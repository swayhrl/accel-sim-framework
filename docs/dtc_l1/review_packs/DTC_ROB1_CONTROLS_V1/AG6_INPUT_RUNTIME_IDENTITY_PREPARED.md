# AG6 read-only input/runtime identity module

`ag6_input_runtime_identity.py` is **PREPARED_NOT_EXECUTED**. Its only public entry is `validate_identity(binding, point) -> receipt`; failures raise `IdentityReject`. No CLI, import-time action, subprocess, signal, lock, output write, process discovery or resource scan exists. No file was executed or imported for this delivery. No test, compiler, fixture or simulator was started. This delivery changes only ROB1's own pack.

The parent must review and bind the exact module and binding JSON in its own immutable production source closure. It must call this entry afresh before each point and launch only the returned `validated_argv` and `validated_environment`, after its separate authority/resource/lease/budget gates. The return value is identity evidence, never dispatch permission or historical executor qualification. The interval covers current file checks; it cannot prevent later mutation. The production mapper must still verify actual stopped mappings, and strict must check actual option/version/input/output echoes and natural completion.

## Concrete immutable sources

The four named points and exact UUIDs are read from parent `AG6_FOUR_POINT_IDENTITY_PREREGISTRATION_V2.json`, inspected at coordinator `1f989964f7bb252c3cf3cae7bb3ec3e9dfde11b2`, byte SHA256 `844591f608ff99203b22f7f7cb958e1c7633726c3e351da7b7407dd53edee38e`. The module fixes that hash independently of caller data. Changing that preregistration requires a reviewed source-pin update, not accepting a caller's replacement digest.

Five evidence objects come from immutable Framework `2f3a8c4b27780e2bf3818949a6e5356d9fd62327`, under `docs/dtc_l1/review_packs/DTC_LANE_AG3_AE_AD_SCREEN_V1/`:

| Binding artifact key | Published file | SHA256 |
|---|---|---|
| `input_stats` | `INPUT_STAT_IDENTITIES.json` | `35700a52c852a81fabd26c0fb28d220be98646f5ca3d46fde7c9191f65aadd89` |
| `input_members` | `ORIGINAL_MEMBERS_SHA256.tsv` | `c1412fd32722f8c95a45c30242d2dfd1abb3b45f4673b5beb3edd27af63c6bc5` |
| `sources` | `SOURCE_FILES_SHA256.json` | `c238c7908f1769a148973019af51c255a0357df7ad9f1764f8ff4c18ef65d79b` |
| `build` | `NEW_BUILD_IDENTITY.json` | `0f66fb68264ac061b4800b7c134b82d7a73b10e96d3993dc59fdea552826142a` |
| `runtime` | `RUNTIME_MAPPING_MANIFESTS.json` | `b417b486017a281c46df924cf2791afdb5378000188c64382fe116df76b0f84b` |

The two actual BASE option/input receipt-facts objects come from Framework `f8cbc9d250cc66cf84547f3fe024691d5ca62934`, unchanged in the later `13c08ad37445ba8bc1dc32862a18861a091bd12e` review, under `docs/dtc_l1/review_packs/DTC_LANE_AG6_V2_PREP_GATE_V1/`:

| Binding artifact key | Published file | SHA256 |
|---|---|---|
| `BASE_GEMM` | `BASE_GEMM_RECEIPT_FACTS.json` | `1ace49e4e93e2251e04434dcf28761002dabeb8601c12c14f33be82a1c155c95` |
| `BASE_Gaussian` | `BASE_GAUSSIAN_RECEIPT_FACTS.json` | `9bbfad8fc70fb54b02dfc406e57bfed9d9373bf1143950e667f28a716fbf18d2` |

These are local copies of immutable published metadata, not old raw input paths. Every descriptor is verified against the independently fixed digest in the module. No caller `PASS`, `stat_unchanged` or `matches_frozen_SHA` string can replace checks. Parent intake currently includes the BASE dossiers and the independently published closed-event join; this module does not turn dossier eligibility into execution authority or re-open raw ancestry evidence.

The input method follows the actual AG3 `tools/strict_screen.py:151` `input_identity`: trace-list SHA plus each historical fresh-SHA member's current device/inode/size/mtime_ns/ctime_ns. It strengthens the glue by joining all 511 stat-provenance rows one-for-one to the independently pinned original SHA table, full ordinal/path populations, both command vectors and full input instruction/CTA totals. It checks member stats both before and after the other identity work. It **never opens a trace body**, and the receipt says `stat_stability_not_fresh_trace_body_hash=True` and `trace_body_bytes_read=0`. This is preservation of known SHA provenance under unchanged stat identity, not a new trace-body SHA measurement.

## Binding object required from parent

```json
{
  "preregistration": {"path": "/absolute/AG6_FOUR_POINT_IDENTITY_PREREGISTRATION_V2.json", "sha256": "844591f608ff99203b22f7f7cb958e1c7633726c3e351da7b7407dd53edee38e"},
  "artifacts": {
    "input_stats": {"path": "/absolute/INPUT_STAT_IDENTITIES.json", "sha256": "fixed digest above"},
    "input_members": {"path": "/absolute/ORIGINAL_MEMBERS_SHA256.tsv", "sha256": "fixed digest above"},
    "sources": {"path": "/absolute/SOURCE_FILES_SHA256.json", "sha256": "fixed digest above"},
    "build": {"path": "/absolute/NEW_BUILD_IDENTITY.json", "sha256": "fixed digest above"},
    "runtime": {"path": "/absolute/RUNTIME_MAPPING_MANIFESTS.json", "sha256": "fixed digest above"},
    "BASE_GEMM": {"path": "/absolute/BASE_GEMM_RECEIPT_FACTS.json", "sha256": "fixed digest above"},
    "BASE_Gaussian": {"path": "/absolute/BASE_GAUSSIAN_RECEIPT_FACTS.json", "sha256": "fixed digest above"}
  },
  "source_roots": {
    "Core": "/workspace/worktrees/gpgpu-sim-iscas2027-dtc-lane-ag3-aead-core-174-v1",
    "Framework": "/workspace/worktrees/accel-sim-iscas2027-dtc-lane-ag2-loader-manifest-174-v1"
  },
  "own_config_copies": {
    "AE_GEMM": [{"path": "/workspace/dtc-evidence-closure-20261019-v1/coordinator/ag6-v2/.../config-0.config", "sha256": "exact original config SHA", "source_path": "exact preregistered original config path"}],
    "AE_Gaussian": [], "AD_GEMM": [], "AD_Gaussian": []
  }
}
```

This is a deliberately incomplete schema example, not executable registration. Each selected point needs four distinct config-copy entries in the original order with original source path/SHA. All own copies must resolve under coordinator `ag6-v2`; the function also rehashes the original config bytes. The parent still needs to freeze/materialize its own config copies and mapper manifest. Missing copies/material, a different preregistration or any identity mismatch fails closed. The shown source roots are original c8090115 / 8e43 source worktrees, rather than the new ROB1 or SEM1 diagnostic source; all recorded 650 Core and 52 Framework source files must still match current byte SHA.

The original build's `combined-final/compile_commands.json` and `trace-final/compile_commands.json` are read at their actual original build paths and checked against `NEW_BUILD_IDENTITY.json`. All 12 deduplicated runtime files from the original mapping manifests must match original SHA and complete recorded stat identity, including loader/cache/helper roles. Byte identity to the immutable ELF/build receipt binds the historical build IDs without running `readelf`, a loader or a simulator. No newly compiled library may substitute.

All 270 expected options are compared to the frozen actual same-input BASE dictionary after exactly one permitted AE or AD 0→1 toggle; the declared delta must equal that change exactly. The return marks `option_basis=FROZEN_ACTUAL_BASE_PLUS_EXACT_SINGLE_ARM_DELTA` and `runtime_echo_observed=False`. A prelaunch function cannot observe a future run's 270 printed option echoes. Config bytes and original defaults/runtime are bound here; actual new echoes remain the production strict parser's responsibility.

Reads are bounded at 64MiB per non-trace regular file and 512MiB total; per-file before/open/after/end signatures reject ordinary mutation or replacement. Receipt size is small (the two command vectors and 12 runtime records, not 702 source bodies). It contains the canonical binding digest, fixed artifact digests, point/UUID, validated argv/environment, own-copy vector, option dictionary digest, counted source/member/runtime checks and monotonic interval. No receipt file is written by the module. Static preparation is complete; current identities and runtime behavior are **NOT_TESTED**.
