# C16 OLMoE V40 final local producer status

Status: `LOCAL_PRODUCER_CLOSED / NODE164_NOT_YET_ADMITTED`

The CPU-only re-audit of the immutable 243-shard portfolio passed.

- 243 selected statics: 129 `EXECUTED`, 114 `ZERO_EXECUTION_PROVEN`, 0 failed/excluded.
- `dynamic_warp_records`: 132,096.
- `active_lane_events`: 4,196,352.
- Typed anchors: weight=101, input=103, output=1085.
- Evidence is conditioned on actual-JIT variant A.

Selector provenance was repaired with `C16_SELECTOR_CANONICAL_V1`:

- raw selector SHA: `d70035debd62f0821f7b4b0c802ecdd3ca101b7213eafb591b3cc56438a271eb`
- canonical V1 SHA: `cb20c01619acf563de69776a7a098b21c31c6ce6d836ea0bc0beab9fe42c979b`
- V38 `9d2d4149…` remains `OPAQUE_HISTORICAL_CHECKSUM_SERIALIZATION_NOT_DURABLY_RETAINED`; it is not claimed as independently reproduced.

P5 re-audit identity closure:

- tool SHA: `2a809952d482f5c79e14093aef8f954aa32e31f78e8daba9aec8d49953780b73`
- canonical replay SHA: `2af88f085fca9a95116158c24c814cf7163bc52a00f18c9968d32a8432791aba`
- function identity SHA: `455068a5b79a00d1e3e2db6297964fd801471fb92a7db6b1cc0b37e5b94dab40`

The bundle must be published only using Pipeline V1 to `hrl174new` inbox `.partial`. No positive ACK, raw promotion, catalog admission, or node164 acceptance has occurred.
