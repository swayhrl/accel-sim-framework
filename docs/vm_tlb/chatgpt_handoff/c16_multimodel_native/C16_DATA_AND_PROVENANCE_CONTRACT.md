# C16 Data and Provenance Contract

## 1. Identity hierarchy

Every scientific row must be traceable through:

`model repo + immutable revision + tokenizer revision + implementation/backend + dtype/quantization + scenario + input hash + run ID + tool/config version`.

Do not use a model-family name as sufficient identity. Runtime measurements must additionally record GPU model, UUID if available, driver, CUDA, PyTorch/framework, attention backend, compile/graph state, and profiler mode.

## 2. Evidence tiers

Allowed tiers:

- `STATIC_SOURCE_BOUND`: immutable config/header facts.
- `NATIVE_BASELINE`: unprofiled real-GPU timing/memory.
- `NATIVE_PROFILED`: nsys/ncu measurements with tool scope.
- `NATIVE_ADDRESS_CAPTURE`: NVBit/memory observer address evidence.
- `TRACE_DERIVED_STRUCTURAL`: offline page/line/set metrics from qualified capture.
- `RETROSPECTIVE_SIMULATOR`: frozen C12/C13 calibration only.
- `UNRESOLVED`: unavailable or ambiguous.

Never promote one tier to another by inference.

## 3. Deployment identity

A deployment differs if any of these materially change:
- model revision;
- runtime framework/kernel implementation;
- weight dtype or quantization method;
- activation/KV dtype;
- attention backend;
- KV representation/layout;
- TP/PP/EP;
- graph/compile mode when it changes kernelization.

Raw and AWQ are separate deployment identities even if they share a named family.

## 4. Scenario identity

Each scenario must record:
- batch;
- requested prompt tokens and actual per-model token count;
- decode length and sampled decode-step bins;
- input corpus item and text/token hashes;
- seed;
- warmup policy;
- logits policy;
- cache/prefix/speculative/continuous-batching status.

The first C16 matrix keeps prefix caching, speculative decoding, continuous batching, and multi-GPU deployment off unless explicitly versioned as a later scenario.

## 5. Kernel catalog minimum fields

`run_id, deployment_id, scenario_id, phase, decode_step_bin, device, context, stream, correlation_id, launch_ordinal, kernel_name, implementation_key, grid, block, start_ns, end_ns, duration_ns, operator_class, layer_id, shape_key, dtype_key, semantic_evidence, mapping_status`.

Never join a second run by naked kernel ordinal alone. A second-pass target must be revalidated by semantic/implementation/shape/grid/block context before capture.

## 6. Runtime object map

Minimum object classes:
- `WEIGHT`
- `QUANT_METADATA`
- `KV_CACHE`
- `UNKNOWN_RUNTIME`

Optional classes such as Activation/Workspace require direct evidence; unknown ranges remain unknown.

Object-map events must carry storage/generation identity and evidence for allocation/view/replace/grow/release. Python object destruction is not GPU-release proof. Shared storage/views must not be double-counted as independent payload.

For MLA/compressed architectures record separately:
- `architecture_attention_representation`
- `runtime_kv_representation`

## 7. Address-domain rules

All address-derived rows must name their domain: `GPU_VA_OBSERVED`, `MODELED_SIMVA`, `CHECKPOINT_FILE_OFFSET`, etc.

Forbidden without evidence:
- GPU VA → PA continuity;
- VA 64KiB buckets → hardware 64KiB page mapping;
- address-bucket count → TLB miss count;
- checkpoint file offset → runtime VA/PA.

## 8. Cache-line and ordering rules

For each line metric record line size and active-mask/width semantics. `.traceg` CTA-group file order is not assumed to be global shared-L2 arrival order.

Allowed without global scheduling evidence:
- unique sets;
- per-window line/page counts;
- set intersection/overlap;
- order explicitly preserved within a qualified local stream.

Not allowed:
- calling a naïve file-order scan a real global L2 MRC.

## 9. Sampling contract

Primary V2 strata are based only on pre-outcome native census fields. Candidate mechanism speedup/miss outcomes are forbidden selector inputs.

Certainty units have weight 1. Ordinary stratum additive estimator:

`Y_hat = sum(certainty Y_i) + sum_s (N_s/n_s) * sum_{i in sample_s} Y_i`.

Rates must be recomputed from independently weighted numerators and denominators. Unique-set union is non-additive and must not be estimated with the same formula unless a separate set estimator is explicitly implemented and validated.

Deterministic medoid selection does not receive a fabricated statistical CI.

## 10. Cross-model wording

- `cross-model common pattern`: same metric/method, same-direction result in >=3 independent model lineages.
- `family-level pattern`: supported within one family across >=2 deployment/scale points.
- `deployment-specific`: one deployment/implementation only.
- `association`: confounded pair.
- `causal`: only for a genuinely controlled intervention.

## 11. Git / raw-data policy

Commit only small source, manifests, summaries, receipts, hashes, scripts, and review tables. Do not commit model weights, profiler databases, large NCU reports, raw SASS/address traces, or simulator logs.

Large data stays in scratch/exchange storage and is represented by `RAW_INDEX.tsv` containing path/host, size, SHA256, producer run, transfer receipt, and retention state.

Cross-lane scientific consumption is fixed-commit + manifest/hash bound. Never consume another lane's uncommitted partial directory.