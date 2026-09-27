# C16 paper story prefreeze V1

Status: `STORY_PREFREEZE_ONLY`. This is an evidence-led argument outline, not Paper/Evidence V2 or an accepted mechanism result. Claim authority remains the frozen Lane 3 ledger and native result table; literature context comes from LR03–LR05 at `350e4a0d364d65812f379ebc69412696e2a4d82a`.

## Problem chain

1. **Quantization-induced residency opportunity.** The deployed packed AWQ footprint in the tested semantic profile falls below the RTX 4080 L2 capacity, whereas the matched dense FP16 weight exceeds it. This is capacity geometry and a plausible opportunity, not a proof that bit width alone causes every traffic change [E1-001, E1-002].
2. **Local residency is real in the bounded experiment.** Memory-state intervention and targeted CUDA persistence alter target timing/traffic and recover local timing value. The strict reversibility and natural DRAM gates remain bounded as recorded [E1-003, E1-005].
3. **Natural full-model traffic destroys the isolated warm condition.** A full-model reuse interval changes the target's observed state; role and layer matter. The tested points establish the phenomenon, not an exact physical cache knee or a unique L2 cause [E1-004].
4. **Coarse/broad persistence restores local benefit.** Rotating shared protection, greater layer coverage and broader FFN-family targeting preserve selected local value [E1-006–E1-008].
5. **Local residency is not system benefit.** The native budget closure measures local savings alongside offsetting other semantic work; representative self-attention NCU does not isolate the aggregate cause. More protected hits or lower DRAM bytes alone do not prove fewer critical cycles [E1-009, E1-010, E1-015].
6. **Separate every conversion step.** `oracle target → protection eligibility → protected admission → old-address survival → next-decode useful hit → local timing → full reuse-window timing`. Class occupancy is not line-generation survival; a miss followed by refill can yield same-class occupancy and later kernel-local hits. The accepted native ledger closes early/local/system observations, while the Lane 4 canary must test the intervening simulator chain.
7. **Ask which existing capability is enough.** `PRIORITY_ALL` challenges simple priority; `PRIORITY_STABLE` challenges whether stable selection alone makes the hard quota unnecessary; DRRIP challenges generic anti-thrash; SHiP-SW-style challenges region-aware learning with equal information. R0 anchors default behavior, M1 tests elastic bounded protection, and M1F is conditional on the terminal review. This comparison separates information, admission, survival and cost rather than rewarding a mechanism name.
8. **Mechanism conclusion waits.** Only an admitted terminal Lane 4 result, project-reviewed A/B/C/D interpretation and relevant strong-baseline comparisons can establish a C3 mechanism claim. The 1565-kernel D1-to-D2-L0 window is a bounded reuse canary, not whole-model steady-state throughput.

## Candidate contributions

| Candidate | Current defensible statement | What still blocks stronger wording |
|---|---|---|
| C1 — Quantization-Induced Residency Opportunity | The accepted deployment and semantic NCU evidence identify a packed footprint and local residency opportunity | Pure bit-width causality, other backends/models and general cache residency remain unproved |
| C2 — Local Residency != System Benefit | Accepted native intervention, broad-protection and run-aligned cost/benefit evidence quantify the local-to-system gap | A unique replacement/cache cause for the offset remains unestablished |
| C3 — Reuse-Survival-Oriented Residency | A **candidate** question: can finite, selective protection retain old useful lines and improve the bounded window beyond equal-information simple/learned baselines? | Lane 4 terminal admission, old-address identity where needed, materiality review, M1F gate and strong baselines |

`Cost-aware` denotes the objective of net benefit, not an already implemented per-cycle utility predictor. `Oracle` isolates an address-identity counterfactual, not a deployable classifier. CUDA persistence does not reveal NVIDIA's internal victim rule; parser compatibility does not prove full Ada timing fidelity; bounded trace tensors are not an absolute-cycle calibration to an earlier native run. These frozen Lane 3 boundaries remain binding.

The literature already contains priority hints, scan-resistant replacement, signature learning, capacity borrowing, stable subset ideas, GPU over-protection observations and cache-resident LLM systems. Therefore this prefreeze does **not** claim first priority/pinning, first fractional admission, first cache-resident LLM, first ordinary borrowing or first discovery of over-protection thrashing. Contribution language will depend on the exact remaining limitation and matched evidence, not on chronological M1→M1F development history.
