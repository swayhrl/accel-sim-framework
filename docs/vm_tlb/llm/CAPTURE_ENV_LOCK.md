# Route-E capture environment lock

Status: prepared in M4A-PR; no host has been rented and no model weight has
been downloaded. This lock is deliberately independent of an AutoDL page's
displayed CUDA 13.x image label.

## Immutable inputs

| Component | Frozen value |
|---|---|
| Python | 3.10.x (primary: 3.10.16) |
| PyTorch distribution | 2.6.0, CUDA 12.6 wheel index `https://download.pytorch.org/whl/cu126` |
| PyTorch runtime provenance | record `torch.__version__`, `torch.version.cuda`, wheel filename and `pip freeze` at capture time |
| CUDA toolkit for NVBit build | 12.6.x local toolkit, explicit `CUDA_HOME`; never change NVIDIA driver |
| Transformers / Accelerate | 4.51.3 / 1.6.0 |
| Safetensors / huggingface_hub | 0.5.3 / 0.30.2 |
| NVBit | 1.7.6, `https://github.com/NVlabs/NVBit/releases/download/v1.7.6/nvbit-Linux-x86_64-1.7.6.tar.bz2` |
| NVBit SHA-256 | `dba61708b702ff4562343716bb8b38a2d14aae5991b9719aece097afe505467f` |
| Framework handoff base | `51a36b376a8c6a59c02c181b26233bd0c4c3322f` |
| Framework Route-E package commit | `524cb20785ec4632b434a0786181ff814ad7eaba` (checkout must be this commit or its reviewed descendant) |
| Route-E artifact digests (SHA-256) | `run_llama_tp4_rank0.sh` `cc38edf0eda9b4498ce639145618770f44e417563799be26b1ac50af29380829`; `rank0_nvbit_exec.sh` `02d34b01c44d9b11abe281addba7b2bda7488175305c42f9b246c5525ff8bbba`; `llama_tp_workload.py` `de8cf872e9ba3aca8390b913441dde65acf2161bb03352b73ed36982d63b7c63`; `run_m4a_c.sh` `1f1a8dff9ae38bf1cde3125f0e162175b60219e2766620d20c041e1845a82492`; `bootstrap_route_e_nvbit.sh` `de78fcd105d809ff35e4819826435c821e74f7bc5cb50251291fec9f51be19f3`; `build_nvbit_with_toolchain.sh` `070a842ec3e0e03f5a6e2a8281a96ab3c051d2f230163a9d6e0d6c351100a5ee`; `classify_kernels.py` `a23c05ebd1b8494cb9a80d0d65ae153a1a76eeb0f1da98f4a21ef5b386983374`; `run_generic_nvbit_smoke.sh` `a11341806c92113cb9be3b6b8ad31af36902569be89844240fbeb6a59abbf371`; tracer `tracer_tool.cu` `414bdeebebf807a1134a53079ed0b7eee47e7fb3eda72250da25b445f5876ab4` |
| Model | `meta-llama/Llama-3.2-1B` at `4e20de362430cd3b72f300e6b0f18e50e7166e08` |
| Capture dtype | `bfloat16`, an explicit self-capture choice; paper dtype is `PAPER_DETAIL_UNAVAILABLE` |

The model revision was obtained through the Hugging Face model metadata API;
no model file was requested. A future gated-model request uses `HF_TOKEN` only
from the process environment and must not log it.

## Local-snapshot transport contract

For the authorized retained-host resume, the exact frozen snapshot may be
transferred from the main server rather than downloaded by the rented host.
The route requires both `M4A_MODEL_LOCAL_PATH` and
`M4A_MODEL_LOCAL_MANIFEST`. The latter is an
`m4a-local-model-snapshot-v1` SHA256 manifest with canonical model ID and
frozen revision. When this route is selected, the workload passes the local
directory to Transformers with `local_files_only=True`; it cannot silently
fall back to Hugging Face. The sidecar and workload manifest preserve the
canonical ID/revision plus the snapshot-manifest SHA256. The manifest is
verified source-to-destination before workload execution; the runtime checks
the selected files and manifest identity without rehashing multi-GiB weights
on every rank.

`resolve_model_metadata.py --dry-run` is safe now. Its non-dry-run mode calls
only `HfApi.model_info`, records the revision and visible config dtype if any,
and never calls a model-file download API. A declared config dtype is not paper
provenance and does not override the explicit self-capture dtype above.

## Selected compatibility route

Primary: an isolated Python 3.10 venv with the PyTorch 2.6.0 CUDA-12.6 wheel,
and an independently installed CUDA 12.6 toolkit for building the existing
NVBit tracer. The runtime's CUDA libraries and `nvcc` toolkit are recorded
separately. This is supported by PyTorch's 2.6.0 CUDA-12.6 installation
instructions and avoids treating a host's CUDA 13.x label as a project lock.
Fallback: the same package pins with PyTorch 2.6.0 CUDA-12.4 wheel and an
explicit CUDA 12.4 toolkit, only after repeating the generic smoke and all
preflights; it is a new lock record, not an implicit substitution.

Hugging Face documents Llama as a tensor-parallel architecture and supports
`tp_plan="auto"` launched by `torchrun`; source/runtime four-rank success is
still a future M4A-C gate. See the authoritative [PyTorch 2.6.0 wheel
instructions](https://docs.pytorch.org/get-started/previous-versions/) and
[Transformers tensor-parallel guide](https://huggingface.co/docs/transformers/perf_infer_gpu_multi).
NVBit's pinned release is listed by [the NVBit project](https://github.com/NVlabs/NVBit/releases).

Pinned-source inspection (without installing Transformers or fetching model
weights) also checked the immutable
[`v4.51.3` Llama configuration](https://raw.githubusercontent.com/huggingface/transformers/v4.51.3/src/transformers/models/llama/configuration_llama.py),
which defines `base_model_tp_plan`, and the matching
[`modeling_utils.py`](https://raw.githubusercontent.com/huggingface/transformers/v4.51.3/src/transformers/modeling_utils.py),
which accepts `tp_plan="auto"` and requires initialized Torch distributed.

## Exact future installation record

```bash
python3.10 -m venv .venv-route-e
. .venv-route-e/bin/activate
python -m pip install --upgrade 'pip==25.0.1'
python -m pip install 'torch==2.6.0' --index-url https://download.pytorch.org/whl/cu126
python -m pip install -r util/llm_trace_capture/requirements-llama-tp4.txt
python - <<'PY'
import torch; print(torch.__version__, torch.version.cuda)
PY
```

Do not use an unqualified package update, `latest`, conda CUDA metapackage, or
driver installer. The capture host reports the existing driver; only the
isolated runtime/toolkit above is installed.

## Compiler provenance contract

Every capture-ready invocation supplies `--cuda-home` explicitly. The selected
`$CUDA_HOME/bin/nvcc` and `$CUDA_HOME/bin/ptxas` must both resolve to CUDA 12.6
and are recorded with their full versions. The bootstrap passes those exact
paths as Make variables and prepends only that toolkit for the build subprocess;
host `PATH` values are recorded separately and may disagree without becoming a
fallback. The tracer source digest above includes the M4A-PR2 fix that prevents
ROI-inactive HtoD memcpy records entering the formal replay list.
