# Retry570 Llama NVBit disambiguation closeout

Status: `NVBIT_RETRY570_LLAMA_MODEL_CANARY_INCONCLUSIVE_FILTERING_NOT_DISAMBIGUATED` with substatus `FAIL_CLOSED_ORDINAL_CONTRACT_CONFLICT`.

This checkpoint supersedes only the scientific interpretation of the earlier
`retry570_llama_model_no_go` closeout; that package and every historical
attempt remain retained and hash-addressable. The former no-go inference is
not carried forward because its valid official/C16 trials used static
instruction intervals `[0,1)` and `[0,8)` (and the C16 trial used
`DYNAMIC_KERNEL_RANGE=1`). A missing memory record from those intervals did
not distinguish a non-memory static interval from a model-level callback
failure.

The frozen contract for the sole admissible disambiguation result is exactly:
candidate kernel `indexSelectLargeIndex`, candidate grid ID `1`, target global
memory instruction `LDG.E`, static ordinal `348`, and `INSTR_BEGIN=348` /
`INSTR_END=351`. The one P0 Llama S0/TEXT binding remains B1, prefill 128,
decode 4, `float16`, eager/uncompiled `sdpa`, no CPU offload, with output
checksum `c5f81e7f7d848bf7d317b15bb2d71471ff3572454fb96f78d877c58ada7f6d65`.

An already-completed, bounded historical launch used `[34,35)`. Its `34` came
from an SM86 SASS-text instruction-line counter for an `LDG.E` in the
hash-bound code object; the later frozen authority requires ordinal `348`.
No equivalence between those ordinals has been established. It therefore is
retained only as an `UNQUALIFIED_ORDINAL_34_ATTEMPT`, never as the required
348-to-351 test. It timed out at 180 seconds before a `MEMTRACE` launch/record,
model-forward receipt, or target-launch proof was emitted. In particular it
cannot prove either coverage or a covered zero-record result for ordinal 348.

Because no official result matched the required contract, the C16 tracer was
not run, there is no disambiguated NO-GO, and no Qwen package or C frozen
target is authorized. Everything here is `scientific_eligible=false`, is not
native-timing evidence, and is not a C selector or H memory-fingerprint input.
Raw payloads remain outside Git and are bound by `RAW_ARTIFACT_INDEX.json` and
the dual-endpoint transfer receipt.
