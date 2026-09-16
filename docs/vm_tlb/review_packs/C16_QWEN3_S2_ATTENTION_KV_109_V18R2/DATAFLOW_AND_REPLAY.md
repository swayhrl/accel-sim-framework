# Typed dataflow and replay gate

Instrumentation patches only the pinned eager attention implementation and surrounds K `repeat_kv`, V `repeat_kv`, QK matmul, softmax and AV matmul with NVTX ranges. The instrumentation-only run is bitwise equal to the qualified uninstrumented replay. The dataflow receipt records tensor shape, dtype, stride, data pointer and storage identity at every handoff.

Established lossless chain:

`PREEXISTING_KV_STORAGE -> POST_UPDATE_KV_STORAGE -> KV_DERIVED_REPEAT_BUFFER -> ATTENTION_CORE_OPERAND`

K and V post-update cache storage are non-aliasing from their repeated buffers; QK consumes the K-derived repeat tensor and AV consumes the V-derived repeat tensor. The direct K-repeat candidate is Class A only: it reads original/post-update K storage. Class B core evidence is explicitly described as derived-buffer evidence, never as a direct cache-storage read.

Dedicated K-repeat replay passes with cache length 2048 before and 2049 after, repeat output bitwise equal, and nonaliasing source/destination. The NSYS signature is the same direct-copy kernel in the in-context `C16_V18R2_KV_REPEAT_K` range and dedicated replay: grid `(16392,1,1)`, block `(128,1,1)`.
