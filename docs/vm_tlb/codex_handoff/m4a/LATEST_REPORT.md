# M4A-C Goal closeout report

Stage: `M4A_C_FORMAL_CAPTURE`

## POSTCAPTURE_REVIEW_PASS_SAFE_TO_POWER_OFF

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

The reviewed final Framework SHA is `c79f4469c6a2befa59e4c4efcd3c885dc2259a81`.
Formal prefill `m4a-llama-prefill-20260902T182016Z` (724 raw/724 traceg) and
fresh formal decode1 `m4a-llama-decode1-20260903T004138Z` (772 raw/772 traceg)
have independent checksum-verified main-server archives. Decode1 SHA256 is
`5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`; prefill
SHA256 is `f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`.
Both have real Weight/KV sidecars (one flat Weight allocation, 128 KV events),
no synthetic KV, retained raw/full lists, and bounded frozen-parser starts on
ordinary compute kernels. The AutoDL balance shutdown after G3 is recorded as
`INFRASTRUCTURE_INTERRUPTION / AUTO-DL_BALANCE_SHUTDOWN`, not a capture failure.
RF0 independently reverified both main-server archives and all required
non-regenerable evidence. `SAFE_TO_POWER_OFF`.
