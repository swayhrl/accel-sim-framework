# START HERE — AWMA R24 tied-weight gradient lifetime native validation

Date: 2026-10-02

Stage:
`AWMA_R24_TIED_WEIGHT_GRADIENT_LIFETIME_NATIVE_109_V1`

Execution branch to create on node109:
`hrl/awma-r24-tied-weight-gradient-lifetime-native-109-v1`

Handoff branch:
`hrl/awma-r24-tied-weight-gradient-lifetime-native-handoff-v1`

Scientific parent:
`6a094ccf28b708d8f8c6419cbdc516922082aa39`

R23G is complete and STOP. Lane F/R22F1 and Lane E/R22E remain STOP. R20 remains CLOSED.
This is the only newly authorized AWMA GPU task. Do not restart R23G or reopen old lines.

## Scientific question

On one frozen real Qwen2.5-0.5B tied-weight training microstep, does delaying the dense classifier-gradient contribution until the input-embedding contribution is ready, and then avoiding a full VxH gradient materialization with bounded row tiling, provide a net time and/or memory benefit after all required recomputation, compact lookup-gradient construction, merge, and AdamW update costs are included?

This is a bounded software/dataflow validation.
No hardware claim, full-training convergence claim, second shape/model, NCU/NVBit/SASS, or Accel-Sim work is authorized.

## Frozen authorities to reuse

- Model: Qwen/Qwen2.5-0.5B-Instruct
- Model revision: `7ae557604adf67be50417f59c2c2f167def9a775`
- Model safetensors SHA256: `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`
- Accepted training-token authority: `ACCEPTED_R101_TRAIN_DISCOVERY_256`
- Token file SHA256: `000404d45d04a183379bd7ffa27efdfc196a08f4f97f2003cabad705ab8e2e6d`
- Exact input: 256 tokens; `input_ids=tokens[:-1]` (255 positions), `labels=tokens[1:]` (255 positions)
- input_ids SHA256: `f59446f6a177507048cad5e272d03b1d910337bf0e626f4ce78aa8c244837a1e`
- labels SHA256: `c89b22206d04b19d9a018e25c732aa5b1acf01b7b1ca18579bfc9ac4e1214f3a`
- Shape: B=1, T=255, H=896, V=151936
- Runtime must re-prove that input embedding and lm_head share the same storage.
- CCE source: apple-aiml-research/ml-cross-entropy @ `3de376c106a1916bc5e1b619f9c77c87a461ee1c`
- Accepted CCE first-store software baseline authority: `ec1ccad7bbcead8853cd97840a2007d96f325aa3`
- Accepted first-store patch SHA256: `e4156b6ec21a7c8696192c9a2ad3eb2196630c72373c64bc8395bc2ef12fda56`

Read the full Goal before changing or running code:
`docs/vm_tlb/chatgpt_handoff/awma/r24_tied_weight_gradient_lifetime_native_v1/LANE_G_R24_TIED_WEIGHT_GRADIENT_LIFETIME_NATIVE_109_GOAL.md`

All CUDA/JIT activity must hold:
`/data/c16/locks/c16_gpu_campaign.lock`

Node164 remains durable raw authority. Do not involve node174.
