# C16 A local preparation and integration — reopened status

Status: `C16_A_LOCAL_PREP_REOPENED_WAVE1_IN_PROGRESS`; this is not a final
closeout and does not satisfy C16-0.9.

Already closed, without any GPU execution:

- C15 metadata/provenance remains read-only and hash-bound.
- C16 input corpus, actual CPU token receipts, and S0–S4 scenarios remain
  frozen.
- Wave-1 Llama3.2-1B and Qwen2.5-0.5B are local, with whole-file SHA-256,
  immutable model revision, and tokenizer revision recorded.  The Llama remote
  LFS lookup is gated, so no unsupported remote-equality claim is made.
- Optional Wave-2 DeepSeek-V2-Lite has four locally present checkpoint files
  (`31,413,626,576` bytes total), each matching the fixed-revision remote LFS
  declaration.

Still active or blocked:

- Wave-1 Qwen2.5-7B raw and AWQ shards are in resumable, range-verified local
  download.  Temporary shards are excluded from the asset manifest until their
  complete-file SHA-256 check passes.
- Immutable `C16_GPU_PACKAGE_P0` is published for the already verified Llama
  assets only. Its own manifest SHA-256 is `ac59f0d2…`; it binds fixed G/C/H,
  frozen inputs/token receipts, S0–S4 scenarios, and the G wheelhouse manifest.
  It neither includes nor stands in for Qwen weights, and it starts no GPU job.
- G `45e293b8…`, C `29e669ec…`, and H `932c6fa4…` are final-consumed only
  after fixed-commit manifest/payload validation.  They provide offline
  environment/wheel/runner and selector/admission protocols, not dynamic
  scientific evidence. Thus the Wave-1 asset gate still prevents publication
  of the GPU package, expected hash ledger, transfer plan, and any rental
  recommendation; no native result, common pattern, cost result, or behavior
  class is published.
- Wave-2 Qwen3-8B remains non-blocking; Qwen3-30B-A3B is explicitly constrained
  by local disk capacity and will not be misrepresented as present.

No GPU, CUDA model execution, profiler, NVBit, simulator, SASS, or full-ROI
task has been started.  The authoritative execution/scientific status, costs,
and gaps are `C16_STAGE_STATUS.tsv`, `C16_COST_MODEL.tsv`, and
`GAP_REGISTER.tsv`.
