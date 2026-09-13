# Retry570 P0 minimal Llama consumption

Status: `P0_MINIMAL_LLAMA_HASH_CLOSED_READY_FOR_MODEL_NVBIT_QUALIFICATION`.

This is an offline/package-consumption milestone, not a GPU measurement and
not a C frozen-target result.  The remote package was intentionally limited
to Llama3.2-1B M1 requirements: the six immutable model files, frozen TEXT
input, S0 scenario matrix, and the exact TEXT/T128 token receipt.  The P0
manifest and all three declared publication-metadata payloads were verified
before binding.  P0's unrelated input/token receipts and its historical G
source payload were not consumed as runtime substitutes.

The runtime source is `40faa7e933b881c1a48593f8eb03c59910b3ba75`; it is the
clean trace-evidence guard commit that must bind the subsequent diagnostic
model forwards.  The remote consumption and token-binding receipts are
retained outside Git with their SHA256 values bound in the two compact
publication receipts here.  No raw profiler/model trace is committed.
