# M4A-C Goal-mode admission report

Stage: `M4A_C_FORMAL_CAPTURE`

## PILOT_PASS_READY_FOR_GOAL_CAPTURE

The current local-model Goal authorization supersedes the historical
credential-only `GOAL_BLOCKED` snapshot. The exact frozen local snapshot of
`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08` was
verified at the rented host by all-six-file SHA256/size checks. No token,
network download, model substitution, synthetic KV, Segmentation change, or
NCCL policy change was used.

R3/P5 real NCCL TP=4, BF16, B=8/S=64/G=3 passed with finite logits and stable
contiguous flat-weight binding. R4/P6 then completed exactly one rank0-only
`DIAGNOSTIC_PILOT` `decode1` trace. It has 772 retained raw traces, 772
postprocessed traces, raw kernel-list preservation, classification, Weight/KV
metadata validation, a self-describing archive, and equal remote/main-server
archive SHA256:

`291dcc3c21ba29579842dd5897995c52887625caaa3342f0f75758242b8bcf98`

The frozen parser Core `73774727e25fadf89df6f30ef5cf014091115db7` initialized
and parsed/started 35 real diagnostic SM86 trace kernels in a 75-second bounded
smoke. This establishes trace-format compatibility only, not a performance
result.

G0 re-admission checks passed on the retained host: framework source
`f994fc9156329b0335f56702dafc2884ce003fe8`, clean working tree, four idle RTX
3080 Ti SM86 GPUs, CUDA 12.6/PyTorch 2.6.0+cu126, and 978 GiB free. The next
authorized action is G2 formal `prefill`, followed by immediate checksum-verified
copy-back before formal `decode1`.
