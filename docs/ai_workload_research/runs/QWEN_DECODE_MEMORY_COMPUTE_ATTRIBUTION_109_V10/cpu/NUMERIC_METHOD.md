# Altered eager sparse numeric analysis

CPU-only analysis loads nine private tensor files using the existing venv and torch.load(map_location='cpu', weights_only=True), sets torch threads to1 and hides CUDA devices. No CUDA/NVML API or vllm import is used. INDEX hashes and recorded runtime Qwen2 source hash are checked before comparison.

Execution was initialized with enforce_eager=True, compile mode NONE and graph mode NONE. Results describe an altered eager path. Internal hooks and selected-row CPU copies can affect execution and timing; this is not native compiled first-layer evidence.

Each runtime sampler request ID is matched by its stable numeric prefix to its private completion request ID, then to source A00/A01. Exact512-token prompt hashes and consumed generated prefixes match across B1/B2. Prefill selected rows are511 in B1 and511/1023 in B2; decode selected rows are0 in B1 and0/1 in B2. Sparse capture selects positions==max and its sampler wrapper asserts equality with logits_indices. Saved max positions are511/512. Full positions, query_start_loc and model input_ids are not saved; the JSON retains this limitation.

Decoder snapshots preserve hidden and residual as separate tensors. hidden is the MLP branch output, residual the skip stream; the source metadata label hidden_plus_residual is not a saved sum. Final RMSNorm tuple index0 is normalized hidden and index1 updated residual. Snapshot cloning prevents later fused-add mutations from changing saved data.

For each matched request/component, compare exact BF16 storage bits and numeric inequality counts. Expand BF16 values exactly to CPU float64, then compute max absolute error, median absolute error with midpoint interpolation including zeros, and RMS. Nonfinite counts are reported. Do not infer logprobs from hidden or sampled IDs.

Six B1/B2 comparisons cover N1 prefill, N2 prefill and the first N2 decode. Four N1/N2 prefill comparisons check both B1 cases and both B2 rows. In all six primary comparisons embedding is bitwise equal and layer0 returned hidden is the first differing sampled boundary. All N1/N2 prefill repeat checks are bitwise equal across the five sampled boundaries. Sampled tokens agree across B1/B2. The evidence localizes only the selected-row observed boundary in this altered path; no operator within decoder0, earlier token/KV cause or native compiled earliest layer is established.
