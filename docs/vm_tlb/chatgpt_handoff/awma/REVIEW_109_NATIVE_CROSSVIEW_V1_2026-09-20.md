# AWMA 109 Native Cross-view Track Acceptance — 2026-09-20

Reviewed execution branch:

`hrl/awma-109-exact-target-native-crossview-v1`

Remote HEAD:

`2122eccc7aed61d05b114075e1c3126c4308e64b`

Status:

`AWMA_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1_ACCEPTED_WITH_SCOPE`

## Accepted exact-target export

All three rows bind the frozen:

- Qwen/Qwen2.5-0.5B-Instruct
- revision 7ae557604adf67be50417f59c2c2f167def9a775
- S2_TEXT
- exact phase / semantic family / occurrence or decode step
- EXACT_WORKLOAD_TARGET relation

Targets:

- T0 Q05_PREFILL_ATTN_FLASH
- T1 PREFILL_GEMM_PRIMARY_OCC0
- T2 DECODE_GEMV_PRIMARY_STEP16

## Accepted producer descriptors

T1:

- raw dynamic records: 12,043,648
- memory instruction records: 2,298,240
- lane addresses: 70,352,896
- 4 KiB pages: 7,906
- 64 KiB pages: 495

T2:

- raw dynamic records: 1,515,136
- memory instruction records: 318,592
- lane addresses: 9,022,720
- 4 KiB pages: 2,132
- 64 KiB pages: 135

## Explicit missing fields

No compact exact-target native duration authority was found for T0/T1/T2.

T1/T2 exact NCU selector/resource evidence was not proven in this stage.

T0 comparable Native footprint fields remain unavailable in the 109 export.

These fields remain explicit UNAVAILABLE and must not be filled from a different evidence class without a separate provenance audit.

In particular, existing Q05 simulator-native trace structure is not silently imported into the Native export.

## Cross-view readiness

The 109 side of the join is considered ready for the current mainline question because the primary purpose is to align:

- exact target identity;
- phase/operator family;
- producer dynamic footprint where accepted;
- later 174 modeled translation sensitivity.

Native timing/NCU are useful but are not mandatory for deciding whether the repaired simulator hit-path sensitivity is systematic across kernel classes.

## Node109 state

The GPU is released.

MoE/AWQ candidate side lanes remain frozen.

No further 109 GPU work is authorized until the 174 Simulation track is available or ChatGPT issues a new mainline task.
