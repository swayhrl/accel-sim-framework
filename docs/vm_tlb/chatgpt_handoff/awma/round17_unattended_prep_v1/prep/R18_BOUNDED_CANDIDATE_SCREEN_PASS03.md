# Pass03 next-candidate screen

Date: 2026-09-30.
Decision: `NO_SECOND_CANDIDATE_QUALIFIED_PASS03`.

After FlowANN closed the active R17 novelty claim, five nearby real-workload families were screened.

| Family | Direct capability | Decision |
|---|---|---|
| structured decoding | XGrammar overlaps grammar work with inference; PSC makes online mask construction vocabulary-size independent | headline mask-overhead problem directly covered |
| sparse/long-context KV | ECHO, HiSparse and PersistentKV cover graph-friendly eviction/recall, exact hierarchical residency, and B1 page-aware scheduling | crowded; no distinct residual |
| logits/sampling | FlashSampling fuses exact sampling into LM-head and avoids HBM logits materialization | direct kernel coverage |
| GPU VM/TLB allocation | MoonBright moves page-table materialization to GPU and defers TLB coherence | high-value related work, but its artifact needs a modified driver and A100/H100-class validated setup; not a cheap 109 falsification |
| VLM visual memory | direct KV/attention compaction exists; recent profiling also questions visual-token dominance | no distinct 109-testable residual identified |

Primary sources:
- https://arxiv.org/abs/2411.15100
- https://arxiv.org/abs/2608.03065
- https://www.usenix.org/conference/osdi26/presentation/liu-guangda
- https://arxiv.org/abs/2608.07009
- https://arxiv.org/abs/2606.26666
- https://arxiv.org/abs/2603.15854
- https://www.usenix.org/conference/osdi26/presentation/zhang-yangyu
- `MoonBright-project/OSDI-26-AE@4cd920295efff73b72e9c28b86e2acd1f3a5bec0`
- https://arxiv.org/abs/2603.23914
- https://arxiv.org/abs/2607.09520

A future R18 card needs: real public input; a residual not already directly targeted; cheap 109 falsification or legal 174 representation; and nearest-neighbor review before mechanism design. No card is created merely to fill the unattended window.
