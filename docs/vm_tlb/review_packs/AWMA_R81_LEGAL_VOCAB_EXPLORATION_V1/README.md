# AWMA R81 legal vocabulary exploration V1

Recommended entry for this review pack. Final state: `R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM`. The bounded authored B4 Qwen2.5-0.5B BF16 experiment ran on node109 RTX4080/SM89. `DECISION.md` gives the scientific conclusion; `REPORT.md` gives the numbers and limits.

## Source anchors and commit history

- Coordination handoff and execution branch base: `785a6c0651a1a4fbc6ed11c829be29d514a13f74`; branch `hrl/awma-r81-legal-vocab-exploration-v1`. The R81 execution commit is the branch HEAD following this base; `git log` on that branch is the exact final history.
- Round08 literature authority: `214b30039cc579c28457cb17bfbd7e9d88d00fcd`.
- Read-only model `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`; safetensors SHA256 `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`.
- XGrammar `0.2.8` wheel SHA and all environment/tokenizer/schema bindings are in `INPUT_RUNTIME_BINDINGS.json` and `ENVIRONMENT_RECEIPT.json`. The prior indexed-head and fused-selection capabilities are mapped in `SOURCE_CAPABILITY_MAP.md`.

## Changed files and validation

- New implementation/tests/fixture: `util/vm_tlb/awma/r81_legal_vocab/`. New compact evidence: this review pack. New report: `docs/vm_tlb/reports/AWMA_R81_LEGAL_VOCAB_EXPLORATION_109_V1_REPORT.md`. No simulator or accepted baseline source was changed.
- `VERIFIED_RUN`: two CPU mapping tests passed; all 480 active request-step dense legal logits were finite; C0/C1/H0 retained all 207 grammar timesteps; A0/A1/A2/A3 selected the same IDs and stop positions; 12/12 JSON outputs satisfied their schemas; one NSYS canary per qualified arm was accepted.
- Formal: 2 warmups and 7 paired/interleaved repetitions per arm/cohort for head region and complete generation. C0's first high-variance full-generation bundle is retained as an attempt, and one exact-configuration repeat is primary.
- `PAPER_SPEC` / `VERIFIED_CODE` boundaries and original versus ported software capability are in `SOURCE_CAPABILITY_MAP.md` and `SOURCE_AND_TESTS.md`.

## Open issues and raw authority

The fixture is authored, not a production distribution. A1 is a bounded greedy adaptation of FlashSampling, and arbitrary dynamic-grammar support in FlashRec source remains unverified. Sparse-state A3 savings did not yield a stable complete-generation gain; software support-aware dispatch remains untested. No NCU or architecture admission followed.

The node164 authority is `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/round08_20260927/R81/`. `RAW_DATA_INDEX.tsv` and `SHA256SUMS` bind all large hidden/mask tensors, compiled grammars, JIT artifacts, NSYS/SQLite and logs; model weights are inherited by hash and not duplicated.
