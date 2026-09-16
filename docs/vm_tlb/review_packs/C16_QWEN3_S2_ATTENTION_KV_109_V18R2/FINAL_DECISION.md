# Final decision

`C16_QWEN3_S2_ATTENTION_KV_109_V18R2_PASS_WITH_SCOPED_EVIDENCE`

PASS scope: one formally captured, Pipeline-ACKed, same-process Class-A `KV_STORAGE_DIRECT_READ` target: Qwen3 layer-0 first-decode `self_attn.repeat_kv(K)` direct materialization. The target is materially distinct from the q/k/v/o GEMV projection paths and losslessly bound to post-update K storage.

Scope limit: QK/AV attention cores were discovered as readers of exactly derived repeat buffers, but were not separately formalized; they are not called direct KV-cache-storage reads. S3 is out of scope. No model, revision, input, precision, backend or semantic-target substitution occurred.

V18 and V18R1 BLOCKED review packs remain immutable attempt history.
