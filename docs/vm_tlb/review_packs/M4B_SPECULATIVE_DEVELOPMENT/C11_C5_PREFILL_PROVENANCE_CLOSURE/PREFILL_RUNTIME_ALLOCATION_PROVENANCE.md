# Prefill runtime Weight allocation provenance

`VERIFIED_RUN`：C11 对 frozen sidecar
`/workspace/m4a-rented-host-pilot/formal-prefill/extracted/m4a-llama-prefill-20260902T182016Z/allocation-sidecar.json`
重新计算 SHA-256，得到
`8b605b8b19034613106a61ab993dcab60b6eb34509293074b123b44ceeaa839a`。

sidecar 的唯一 `WEIGHT` allocation 是：

| 字段 | 值 |
| --- | --- |
| allocation id | `weight-flat-rank0` |
| provenance | `m4a runtime flat-buffer binder` |
| lifetime | `MODEL_LOAD → DECODE` |
| SimVA start | `0x7fd99e000000` |
| bytes | `1,012,011,008` |
| runtime extent | `0x7fd99e000000..0x7fd9da520fff` |
| tensor | `ALL_PARAMETERS` |

这与 A checkpoint 的 `M4C_PREFILL_OBJECT_MAP.tsv` 完全一致：source SHA 为
`08bd106f6597865e622465ee3bd13233f7d49fd1eef131965fd2692956091e7a`，archive
SHA 为 `f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`。

因此 C11 的 privileged registration 从 runtime allocator sidecar 派生。对象 map
只保留为 telemetry attribution；它既不触发、也不决定 Segment eligibility。
