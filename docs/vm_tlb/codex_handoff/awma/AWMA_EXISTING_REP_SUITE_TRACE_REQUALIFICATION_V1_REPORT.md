# Existing representative-suite trace requalification V1

Status: PASS — both exact-safe assets upgrade from `REQUIRES_REQUALIFICATION` to `REUSABLE_NOW`.

Only existing node164 simulator-native payloads were replayed. No capture, mechanism, baseline, source, or Lane B/E input was changed.

| asset | V1 VM | cycles | instructions | CTA | unique UID | status |
|---|---:|---:|---:|---:|---:|---|
| SPLITKV | 10/80 | 73923 | 36599648 | 126 | 233814 | PASS |
| SPLITKV | 0/80 | 74723 | 36599648 | 126 | 233814 | PASS |
| COMBINE | 10/80 | 10480 | 72908 | 2 | 1099 | PASS |
| COMBINE | 0/80 | 10312 | 72908 | 2 | 1099 | PASS |

## Closed identity and gate contract

- Splitkv: `DECODE_FLASH_PRIMARY_1_STEP16`, `FLASH_FWD_SPLITKV`, grid `1,9,14`, block `128,1,1`, step 16, global launch 17543; payload `282a...`, runner/index `5923...`.
- Combine: `DECODE_FLASH_PRIMARY_2_STEP16`, `FLASH_FWD_SPLITKV_COMBINE`, grid `2,1,1`, block `128,1,1`, step 16, global launch 16813; payload `d153...`, runner/index `31b5...`.
- Each V1 point passes payload/index identity; rc/terminal completion; stable instructions/CTA/UID across 10/80 and 0/80; full translated UID coverage; untranslated=0; unobserved=0; duplicate=0; and final MSHR/PWQ/walkers=0.
- Trace grammar receipts provide independent pre-replay grammar counts (splitkv 1,320,771; combine 2,534). They are not equated to `gpu_sim_insn`; the qualification uses the replay counter signature reproduced across both frozen VM overlays.

The baseline is the frozen `RTX4080_ADA_ACCELSIM_BASE_V1` with the V1 frontend only. `10/80` remains model-relative and is not claimed as a hardware TLB latency.
