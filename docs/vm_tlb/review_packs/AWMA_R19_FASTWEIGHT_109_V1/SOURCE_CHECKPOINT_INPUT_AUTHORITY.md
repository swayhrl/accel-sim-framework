# Source, checkpoint, and input authority

## Fixed official sources

`yancyou/TTT-NTP@c11da918d9a5aebf3f3cb0f45a79c2e66d9ad79a` has no release,
tag, or checkpoint asset. Its Qwen3-0.6B path explicitly trains 100 steps,
converts the resulting DCP checkpoint, injects `ttt_*` config, and needs the
trained `ttt_proj.weight`. A base Qwen3 checkpoint is therefore not admissible.

`ByteDance-Seed/In-Place-TTT@be2324829b0e91c8fd10a74d4b43714fde6676e1`
also has no release, tag, or checkpoint asset. The documented path requires
continual pretraining, DCP-to-HF conversion, and inference with trained
`ttt_conv`, `ttt_proj`, and selected MLP down-projections. An arbitrary base
checkpoint is not admissible.

The bounded local/node164 search found no trained TTT checkpoint. It found only
base Qwen3 assets, which were rejected by construction.

## Public third-party candidates

The `zhongweixie/inplace-ttt-qwen3-4b-*` models expose BF16 weights and TTT
weight keys, but the Hub repos contain no custom model code and the linked
source URL returns 404. They were rejected because exact executable
remote-code identity is missing. The separate `inplace-ttt-models` card states
that its originally evaluated checkpoints were deleted.

`hungngo04/gemma-3-1b-it-ttt-tinystories-500k` was admitted only as a
`PUBLIC_REPRODUCTION_ARTIFACT` because the pinned Hub revision supplies:

- a 2,013,140,976-byte BF16 safetensors file with SHA256
  `cc3a8920932dcdd7834867e144caf62c8b45e00410347b89e65d345f6d76e9ed`;
- `auto_map` plus bundled model/config code;
- nonzero trained `ttt_conv` and non-initial `ttt_proj` tensors on layers
  `[0, 6, 12, 18, 24]`;
- explicit adapter-only training provenance, dataset, sample count, and source
  repository.

The associated public source was frozen at
`IntelligentSandbox/Adapter-Only-In-Place-TTT@b6cbb66836b6387f50ac2bf587c5046cc86070f4`.
This is a reproduction with different training scope from the official paper;
it is never described as an official checkpoint.

## Real input

The reproduction harness's HELMET Banking77 generator was used unchanged for
sampling/rendering. The data bytes come from
`PolyAI-LDN/task-specific-datasets@57ec275d8078af65b7731c2a98be812d844a6d6b`.
The generated example is `helmet_banking77_8192_0000`, seed 1337. Its full
prompt SHA256 is `c6b53caabbec3b70ea21e6ae6bcc39ea35eb5a6783d15a6c53f19cbcf17d23a7`.
The fixed natural 256-token prefix has token-ID SHA256
`4c67720dced120bc3b33b62aeb1e5db9e92bedf65d4423b888ff20bb3e819d9a`.
