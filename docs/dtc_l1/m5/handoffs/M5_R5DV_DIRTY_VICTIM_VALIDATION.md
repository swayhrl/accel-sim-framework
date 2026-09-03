# M5 R5DV ratio-zero dirty-victim validation

Status: **PASS — M5-T005 CLOSED**

This handoff closes the approved ratio-zero validation for the frozen 16 KiB,
128 B-line, four-way conventional L1 policy.  It does not alter DTC semantics,
write-through behavior, allocation, replacement, assertions, workload input,
or the retained ratio-25 diagnostic evidence.

## Runtime identity

| field | value |
| --- | --- |
| Core runtime SHA | `22db16b8feb007a405634588b6bec97c935d2ecb` |
| Framework config SHA | `81c75b5d315a29607412a3e28a07c83a2e0a1486` |
| workload | canonical Parboil CUDA JDS SpMV medium `bcsstk18` |
| executable SHA-256 | `08f834ff68e9e092db1f988974ddb8491bba06c176037e862aa81b839ec5900c` |
| PTX SHA-256 | `8e74fe5310962f413d7e29bfb205571a13cb9c7739cd86ebb3b7b1ed51ba39bf` |
| matrix SHA-256 | `abbe1909f57d6fc17fc800446bac326bd0c5343305cf193b3aa1bc8f40c82ec9` |
| vector SHA-256 | `d155de2b9615cae3c2bb8b60a9e82a7d26be7e80de772a5f1c0cb830d2e49061` |
| output checker | `util/dtc_l1/verify_m5_parboil_spmv_output.py` |

All reported runs explicitly set `-gpgpu_l1_cache_write_ratio 0`; the
deadlock detector remains enabled.  Historical ratio-25 jobs and raw outputs
are retained as `DIAGNOSTIC_PLATFORM_POLICY` evidence and are not relabeled.

## Canonical closure results

| mode | config SHA-256 | terminal evidence | cycles | instructions | output check | registry ID | raw log |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| LEGACY | `e49453b37d2bc430abf9bc56caf1f1a10e7d665cd5b9d24f7e919fd65f1f1970` | normal simulator exit; application PASS | 1,343,406 | 121,342,000 | PASS, 11,948 elements | `M5-f43a919958f43224` | `/tmp/dtc-l1-m5-r5dv3-legacy-ratio0-20260904/m5_run.log` (`12b1332ce7893274a42c89c53b1d4d28b7f7d7c4297e1723f1b7b05ac08205cc`) |
| PAPER_BASE | `993513296458bf014cfa33ff047e1ed7391a1fee990e3b4a2d9d738cab0ff366` | normal simulator exit; application PASS | 3,202,814 | 121,342,000 | PASS, 11,948 elements | `M5-eaf5eb9173dbad12` | `/tmp/dtc-l1-m5-r5dv3-base-ratio0-20260904/m5_run.log` (`a10c1e5d4c18a9e655ff98cf221e08afce6c353f3851f3f3a61b953cf773f30e`) |

Both output files have SHA-256
`94148cba6fbed65468efb4317ee255e8f90fec37e1b6a31c706337a02d785127`.

## PAPER_BASE accounting acceptance

The strict parser verified:

- `DTC_L1_pib_admits = DTC_L1_pib_retires = 741200`;
- `DTC_L1_lower_requests_acquired = DTC_L1_lower_requests_released = 3844406`;
- `DTC_L1_pib_occupancy = 0` and `DTC_L1_lower_outstanding = 0` at termination.

The matching compact summaries are
`m5/generated/m5_r5dv3_spmv_{legacy,base}_ratio0.json`; the resumable registry
is `m5/generated/result_registry.json`.

## Prior validation retained

Before these canonical runs, the source-level dirty-set regression, Release
build, all DTC CTests, four ratio-zero VecAdd sentinels, and M4 mixed
Store/Atomic/architectural-`.cg` sentinels passed.  The corrected policy is
therefore accepted as a configuration fidelity correction rather than a
mechanism change.

## Next scope

Resume M5.0B from its existing Paper-10 source/workload recovery checkpoint.
Do not redo valid R5DV or provenance work.  E1 may prepare Extended-20
source/build/input/output identities opportunistically, but its 60-run primary
wave remains blocked until M5.2 PASS.
