# AI-ARCH Round A79: Qwen2.5-3B BF16 native workload sensitivity

Scientific terminal: GPU_RESOURCE_DEFERRED. G0 completed and its contract was frozen before a single nonblocking GPU-lock attempt. That attempt conflicted. G1 and G2 were not admitted. G3 archives the actual negative admission event, then STOP.

Base: 7094d4b2d29980c2d2d8d97a9abb6fddb3283c9f.
Branch: hrl/aiarch-a79-qwen25-3b-native-workload-sensitivity-109-v1.

There was no lock wait, polling, owner inspection, preemption or interference. CUDA initialization=0, NVML initialization=0, model initialization=0, GPU lock-held time=0 seconds and formal samples=0. EXCLUSIVITY_EVIDENCE_COMPLETE=false: a run that never acquired the lock is not an exclusivity success. There are no H0 numerical results, historical timing drift, G2 curves, workload-sensitivity positive/negative observations or hardware conclusions. FORMAL_SAMPLES.tsv has only its header; raw/ADMISSION.json contains the real admission event rather than invented model outputs.

G0 authority

1. Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1, BF16, no quantization, TP1. All 12 published model-manifest files, including both weight shards, were read-only size checked and fully streaming-SHA256 verified. See SOURCE_AND_RUNTIME.json. No weights or datasets were downloaded, and nothing was installed or upgraded.
2. Installed vLLM 0.30.0 compilation.py and qwen2.py hashes match the historical DQ2 pins. Actual libraries: torch2.13.0, transformers5.18.0, tokenizers0.23.2 and jinja2 3.1.6. These actual versions are disclosed separately from the historical CPU tokenizer versions. Current CPU encoding exactly reproduces both historical512-token arrays; this does not assert identical historical compiled binaries.
3. Frozen A00/A01 source byte counts are41457/53757. Their hashes, original512-token JSON file hashes and compact token-array hashes match the old receipts. Historical512 inputs are unchanged; their recorded UTF8 source-prefix sizes are2044/2209 bytes.
4. New2048-token inputs use each same natural source, full chat template, historical prefix bisection and adjacent monotonicity guard, followed by the new Goal's shortest-byte tie break within an equal-token-count plateau. A00/A01 each reaches exactly2048 tokens, with9445/8954 UTF8 prefix bytes. No copying, concatenation, padding or other source was used. Private inputs remain local; Git contains hashes, lengths, indices and attribution, not corpus text or token arrays. No sealed holdout or PG-19 payload was opened.
5. The local historical MP02_A.json reference is available and matches SHA256318326c7fa52dcb7f228d4e2c5be7daddf715f715fc367540fb87f4fad63ab89. This is reference-asset qualification only, not a newly executed H0 output correctness PASS.

License and attribution

The local model LICENSE is the Qwen RESEARCH LICENSE AGREEMENT, with a non-commercial research/evaluation grant. This task is local AI-ARCH research/evaluation without model-material or generated-content redistribution. The pinned WikiText card is https://huggingface.co/datasets/Salesforce/wikitext/raw/b08601e04326c79dfdd32d625aee71d232d685c3/README.md. Its metadata lists cc-by-sa-3.0/gfdl, while its prose names CC BY-SA4.0. This disagreement is explicitly preserved, not silently resolved. Only existing small frozen text was used locally, with Salesforce, WikiText and Wikipedia attribution; no text is republished in Git. The source rows API does not bind commits, so frozen bytes remain input authority.

A direct109 metadata HTTPS request timed out. An independent web-tool read of that exact pinned raw README supplied the selected license-disclosure fields. The recorded disclosure hash covers those captured fields, not a falsely claimed complete README byte hash.

Two bounded pre-GPU engineering repairs were used: metadata transport, then normalization of the installed tokenizer's BatchEncoding return value to its explicit input_ids. The initial failed assertion compared a container with a token list; it did not establish a scientific token-identity change. After normalization both historical512 arrays matched exactly. No model, text, template, precision, installed environment or numeric threshold was changed. See ENGINEERING_LOG.json. The later report-only publication correction below is not a retry or repair of the experiment/runtime.

Frozen experiment and unexecuted tools

FROZEN_SCIENCE_CONTRACT.json predates the lock attempt and freezes H0 plus C01-C08 in the prescribed order; G1 capacity544 and a separate G2 shared capacity2080; two warmups and five formals per point; the exact strong compiled Mode A; historical median354.59820556640625ms; MAD/median<=5%; the15% historical timing-link criterion; and the numerical/resource gates. G1 must never replace G2's short-length point. Prompt/output contrasts and interaction may only use G2's shared capacity. A conservative descriptive difference envelope was frozen as abs(delta)>max(5% of the smaller median,3 times the sum of the two MADs); it is not a statistical significance test, resource axis or saturation threshold. No observations exist to apply it here.

The task-only tool directory contains CPU qualification, a fresh-context worker, an independent nonblocking-lock/NVML supervisor, analysis and offline publication validation. Static cache interfaces use new context-specific VLLM/HOME/XDG/Inductor/Triton/CUDA/HF/Torch roots. Any future generated cache identity would be NEW_MODE_A_COMPILATION_IDENTITY. Since no lock was acquired, GPU compile-cache generation and runtime isolation were NOT_EXERCISED, not passed. Old C16/AWMA contracts, raw, model/environment files and compile caches were not modified.

The supervisor is prepared to sample own PID-tree RSS, NVML own memory/PIDs and task disk approximately every2 seconds, fail closed on external or unknown GPU PIDs, and terminate only its own process group. Its actual lock-conflict path returns before NVML initialization, so there are no device/PID observation samples. The CPU-preparation lifetime aggregate tree-RSS peak was not continuously sampled and is not presented as a measured PASS. Final snapshots and this limitation are recorded in RECEIPT.json. No45-minute,720-second GPU,15400MiB VRAM,16GiB RSS or3GiB disk limit was relaxed.

Next scientific question, conditional only

Current evidence establishes only deferred GPU admission. A new explicit dispatch and an available resource window would be needed for any later lock attempt. No automatic retry or next Goal is started. If a future legal strong-Mode-A matrix exposes a difference worth attributing, one conditional observable resource question is whether the32-output increment at longer prompts exposes additional device-memory service constraints, including KV reads. It would require matched same-input/strong-software memory-service, busy/idle and queue/throughput evidence, separated from an uninstrumented complete-request wall control. Any new intrusive measurement requires separate authorization. Length slopes alone cannot identify DRAM/L2/TC/TLB bottlenecks or manufacturable hardware gains.

Publication correction and STOP

The first19-file commit was4213330affef4aae0c82ba036c8f4ee75816589a. Final remote readback revealed that the local PowerShell input pipeline had converted the intended Chinese report to question marks. This English report corrects presentation and updates payload checksums/receipt; it does not alter frozen inputs, code, the contract, GPU admission evidence or scientific status. The correction requires a second normal documentation push and a second fetch-back, an explicitly disclosed deviation from the Goal's single-publication prescription. No force push, GPU retry, lock polling or new experiment is involved. Final exact commit/tree/all blobs and clean verification are supplied by the independent post-commit proof to avoid self-reference.

Only this A79 tool/output scope is committed. No coordination file, old benchmark sample or other project was changed. There is no simulator, Profiler, trace, new mechanism, node164 access, cleanup or automatic next Round. STOP after final publication verification.
