# Decode1 runtime Weight allocation provenance

`VERIFIED_RUN`：C11 对 frozen sidecar
`/workspace/m4a-rented-host-pilot/formal-decode1/extracted/m4a-llama-decode1-20260903T004138Z/allocation-sidecar.json`
重新计算 SHA-256，得到
`7a07d6715fe79abd24cfc0b12d2619555e0bf472f5285781e098940acefccaa7`。

sidecar 的唯一 `WEIGHT` allocation 是：

| 字段 | 值 |
| --- | --- |
| allocation id | `weight-flat-rank0` |
| provenance | `m4a runtime flat-buffer binder` |
| lifetime | `MODEL_LOAD → DECODE` |
| SimVA start | `0x7f7ec6000000` |
| bytes | `1,012,011,008` |
| runtime extent | `0x7f7ec6000000..0x7f7f02520fff` |
| tensor | `ALL_PARAMETERS` |

这与 A checkpoint 的 `M4C_DECODE1_OBJECT_MAP.tsv` 完全一致：source SHA 为
`44bfae640360be7fc884589c65b261a791e7c388d9d88b7d2742d7eaea7dba4d`，archive
SHA 为 `5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`。

decode1 不是沿用 C10B 三 kernel registration，也没有复用 prefill 的 PA 值。
它有独立 runtime VA、独立 V2 descriptor 与同一确定性 PA policy。
