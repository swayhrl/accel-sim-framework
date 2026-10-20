# Current decision brief — controls and paper closure

E2 remote HEAD checked: `eb889b4077c43cca591afbc5c05eee6beffe5d73`.
The live canonical registry records **22/40 starts, 18 remaining**, four accepted MAIN pairs, and **no accepted control**. Conv W_ONLY (E021_a0d5fc96) and F_MINUS_V (E022_0f3897b6) are running. The original controller PID 2078407/start_ticks 925712542/boot identity matches `/proc`; D has not launched or changed it. The published E STATUS still describes the older 20-start stopped checkpoint; live identity and exact accepted pointers take precedence.

| Input | S cycles | F cycles | Speedup, S/F−1 |
|---|---:|---:|---:|
| Conv | 292932 | 291469 | +0.502% |
| CFD | 79093 | 79157 | −0.081% |
| DWT | 166519 | 167643 | −0.670% |
| SAD | 110773 | 109754 | +0.928% |

Interim four-pair GM: **1.001679 (+0.168%)**. Original seven-input denominator remains seven; its GM is **UNKNOWN**. All pairs use main61 SHA256 `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`, Core `d010911e3174a3764791183cd108fe4664ba8731`, Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`. Exact input/config/receipt/qualification/run-key identities are in `accepted_snapshot_01/CURRENT_ENDPOINT_IDENTITIES.csv` and the approved plan.

## Scope correction

The previous D five-control request is preserved as historical analysis, **superseded as a proposed execution scope**. It grants no authority. Current E-approved preparation is:

| Workload | Controls | Execution boundary |
|---|---|---|
| Conv | W_ONLY, F_MINUS_V, F_MINUS_R, S_COPY_FREE, WV_M, WV_T | Original six controls; first two running |
| DWT | S_COPY_FREE, W_ONLY | Four-cell revision approved; separate E qualifications; wait for original controller STOPPED, exact matrix adoption and live capacity checks |
| CFD | F_MINUS_V, F_MINUS_R | Same approved revision and execution gates |
| SAD | None | W_ONLY is **not approved** |

DWT F_MINUS_R is **not approved**. Approval and qualification of four replacement cells do not mean they have launched or that the active matrix has already changed. No starts, refunds, retry rights or result-budget expansion are added by D. All ten completed controls would yield 30/40 cumulatively; adverse or failed starts remain charged. E's immutable specs contain inherited contingency prose: the actual bucket charges are those in E's metadata clarification and canonical ledger, not that stale prose.

## What the next accepted control can answer

* **Conv:** S→W_ONLY measures net W organization/copy/allocation effects. F_MINUS_V→F measures V at W+RO; F_MINUS_R→F measures RO at W+V. Each includes timing and state interactions. WV four corners are C00=F_MINUS_R, C10=WV_T, C01=WV_M, C11=F. Report T at each M and M at each T as soon as those endpoints exist. Compute `C11−C10−C01+C00` only after all four are current. This signed interaction is not an exclusive cycle decomposition. S_COPY_FREE is a diagnostic, not a hardware design.
* **DWT:** S→S_COPY_FREE is a copy-service counterfactual; S→W_ONLY is net W; S_COPY_FREE→W_ONLY contrasts W organization with that diagnostic. W_ONLY→F identifies only the **joint V+RO conditional net effect**. Neither individual V nor RO marginal contribution is identifiable from the approved DWT set, even after it completes.
* **CFD:** F_MINUS_V→F and F_MINUS_R→F identify different **conditional net effects**, on W+RO and W+V respectively. They cannot be added into independent V/R savings. No W-only CFD counterfactual is approved here.
* **SAD:** its first kernel improves by 989 cycles before either run has observed a copy. Keep that prefix unexplained. Later removal of 3975 copy reads and 3975 copy writes cannot explain an earlier gain. Do not label the full 0.928% gain a measured W or copy contribution.

## Present scientific limits

CFD's 49962 V responses and 51678 avoided line allocations coexist with +64 elapsed cycles. DWT's 23305 V responses, 9965 avoided allocations, 13.845% fewer bank services and 5.575% fewer lower-read bytes coexist with +1124 cycles. These counts establish activation and reduced service demand, not critical-path savings. DWT kernels 5 and 8 account for +1367 cycles; 98.9% of landing wait increments occur in faster kernel 1, and the later two regressions have no new RO queries. Same-bank landing capacity and V/state interactions remain hypotheses; direct sums of overlapping waits cannot explain the program delta.

All four F runs enable T but record **zero successful Tag detach** over all 64 terminal slices; all observed complete intermediate frames also have zero. No observed speedup can be claimed as an executed Tag-detach benefit. Zero successes do not establish zero attempts, zero overhead or a T-off equivalence.

| Evidence class | Supported statement | Limit |
|---|---|---|
| Actual E-accepted statistics | Four cycle pairs, named-kernel elapsed deltas and explicit mechanism counts | No exclusive critical-path attribution or significance claim |
| Frozen-source derivation | Landing requires free/reclaimable payload in the selected bank; V/RO modeled query paths can add latency | Capability/order semantics do not measure their program-cycle contribution |
| Causal hypothesis | State/queue/query interactions may offset service savings; W/V timing may contribute to SAD's prefix | Unmeasured until appropriate accepted controls discriminate it; approved DWT set still cannot separate V and RO |

The interface and ready-to-use EN-v20 candidates are delivered now; no control value is fabricated while runs are active. The English mother manuscript, E ledger, binary and all old results are untouched.
