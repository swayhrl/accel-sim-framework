# Source and runtime anchors

The following values are derived from original per-arm manifests and the
direct runtime-provenance record.  Existing manifests are not rewritten.

| Scope | Field | Value | Evidence |
| --- | --- | --- | --- |
| all_arms | simulator_binary_sha256 | 100527f1d54600dcbbf7c713584512344a688521089aaa995a0b7e4106f81eda | frozen C3 direct binary SHA256 record |
| all_arms | mapped_libcudart_realpath | /workspace/worktrees/gpgpu-sim-vm-llm-m4b-integration/lib/gcc-11.4.0/cuda-11080/release/libcudart.so | direct /proc/<pid>/maps record; supersedes host-path recording error |
| all_arms | mapped_libcudart_sha256 | fc07def22e239de9fec8a3dd83d237a607a82162cab2933d6707a37c0a208b0a | direct /proc/<pid>/maps resolved Core-local runtime SHA256 |
| manifest_lineage | framework_heads | 7709376eb7c7358247e1868f80a143edb54ce69d,a7c0759be7f293ed0d5e2179c62094b6de49c1e8 | original per-arm RUN_MANIFEST.tsv values; never rewritten |
| manifest_lineage | pre_correction_framework_head | 7709376eb7c7358247e1868f80a143edb54ce69d | first three decode arms |
| manifest_lineage | post_correction_framework_head | a7c0759be7f293ed0d5e2179c62094b6de49c1e8 | decode1-paper and all prefill arms |
| manifest_lineage | core_head | 0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd | uniform original per-arm RUN_MANIFEST.tsv value |
| correction_scope | 770_to_a7 | docs plus export_m4c_telemetry.py only | validated Git path scope; no simulator runtime source path changed |

The early decode manifests retain the pre-correction Framework SHA.  The later
Framework-only correction is restricted to docs and the offline exporter; the
provenance table records the verified Git path scope and the common frozen C3
binary/runtime identities.  This is not a claim that the historical manifests
were retroactively changed.
