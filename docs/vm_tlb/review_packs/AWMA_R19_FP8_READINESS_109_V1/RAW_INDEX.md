# Durable raw index

Publication root on node164: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r19_fp8_readiness_109_v1_20261001/`.

`raw/` holds the frozen real projection input/weight `.pt` payload (SHA256 `5ac9e6eb35ec2676926481d563628b80d528dac3dbdbe87bece26d21f4c54b48`), exact input receipt, both canary JSON receipts, stdout/stderr of hook/canary attempts, and environment/build logs. `wheels/` holds the pinned Python package wheel, TE Torch source archive and locally built TE Torch extension wheel. The 645 MB TE CUDA distribution wheel remains on node109 with its SHA256 in `SOURCE_RUNTIME_AUTHORITY.md`, since it is a reproducible upstream package rather than experimental raw. `SHA256SUMS` at the publication root hashes every published file except itself.

The raw canary attempts with missing isolated dependencies (`onnxscript`, `einops`) and their repairs are retained. The delayed recipe is explicitly excluded from formal A1; the current-scaling canary is the final bounded numerical result. No formal timing, NSYS, or NCU files exist by design because F3 stopped the work.
