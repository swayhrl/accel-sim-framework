# V35 existing CUDA static-tool addendum

This addendum supersedes the provisioning/search portions of the V35 handoff where they conflict.

## Known node109 tools

The following tools are already present on node109:

- `/usr/local/cuda-12.8/bin/nvdisasm`
- `/usr/local/cuda-12.8/bin/cuobjdump`

Observed version for both:
`CUDA 12.8.90`

Therefore:

- **do not install CUDA Toolkit**
- **do not download replacement nvdisasm/cuobjdump**
- **do not change the active torch/CUDA runtime**
- **do not globally alter system CUDA selection**

Use the absolute paths above, or temporarily prepend:

`/usr/local/cuda-12.8/bin`

to PATH inside the V35 shell only.

## Required validation

Before relying on these tools, record:

- absolute path
- `--version` output
- SHA256 of each binary
- executable status

Then prove the 12.8.90 tools can inspect the actual code object/module used by the V34-compatible OLMoE expert58 BF16 down-projection execution.

The active model runtime remains the accepted V34 runtime family:
- torch 2.7.1+cu126
- CUDA runtime 12.6
- transformers 4.55.0

The presence of CUDA 12.8 command-line inspection tools must not be treated as a runtime upgrade or deployment change.

If the 12.8 tools cannot parse or unambiguously map the actual target function/code object, fall back to the V35 independent NVBit static-introspection route. Do not install another toolkit merely for version matching unless all bounded existing-tool and NVBit routes fail and a genuine static-selector blocker remains.

## Revised Stage 1 order

1. use the known absolute-path CUDA 12.8.90 tools
2. identify the actual target module/code object/function
3. attempt fresh static disassembly/path classification
4. cross-check with NVBit static introspection when useful
5. once deterministic OLMoE selector closes, continue automatically to canary -> formal capture -> admission/ACK

A missing PATH entry is an engineering setup detail, not a blocker.
