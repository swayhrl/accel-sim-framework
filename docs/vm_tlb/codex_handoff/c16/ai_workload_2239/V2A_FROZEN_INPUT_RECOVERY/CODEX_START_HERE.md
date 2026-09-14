# Codex start here — V2A frozen-input recovery

Run this task on the old/source Docker.

Branch:

`hrl/c16-ai-workload-frozen-input-recovery-v2a`

Read `HANDOFF.md` in this directory completely before acting.

Primary objective: recover the exact historical Llama S0/T128/Decode4 frozen-input five-file bundle and publish it byte-for-byte to Git only if the historical four-hash contract and semantic identity all pass.

Do not run GPU workloads. Do not invoke a tokenizer. Do not regenerate token IDs. Do not alter existing evidence.

Also perform only a bounded locator audit for R5 U5/U6/U9 raw provenance, N1 NCU artifacts, and U8 NVBit artifacts. Do not copy large data.

Commit, push, stop, and report the V2A decision.