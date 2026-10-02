# R27 varied-batch capacity stability plan

Date: 2026-10-03 (Asia/Shanghai)

Handoff: [one gated Lane G/node109 Goal](https://github.com/swayhrl/accel-sim-framework/blob/5144bde8f9d7b399a596395e0c88ee89025b3a6f/docs/vm_tlb/chatgpt_handoff/awma/r27_varied_batch_capacity_v1/LANE_G_R27_VARIED_BATCH_CAPACITY_109_GOAL.md), parent R26 execution `1a2485011b300cddd5137bbccb91dd6d30cfc22f`. Handoff HEAD `5144bde8f9d7b399a596395e0c88ee89025b3a6f`, tree `605f0360debb3f62a1923452c91552ca1f2acaa9`.

## Why this is the next bounded question

[R26 review](../empirical/R26_TIED_WEIGHT_CAPACITY_REVIEW_2026-10-02.md) accepted C1 B70/B71 and S2 B71/B72 five-step boundaries with three confirmations, using repeated copies of one text sequence. The one-batch extension is useful as a software feasibility witness but B70 whole-step peak was 3.828 MiB higher for S2 and both timing regions were MIXED. An OOM in the common backward on step 3 makes the allocator history an attribution question, not an established cause.

The next useful falsifiable test is whether a single **fixed, genuinely varied text stream** preserves a same-B capacity extension and whether S2 runs 32 uninterrupted steps at the witness with correct state recovery. The input is WikiText-2 raw *train* at a pinned source revision/hash, tokenized once with the accepted local Llama tokenizer into a fixed 33×128×128 bank. At each step, B chooses the first B distinct rows. This preserves one physical-batch axis while varying batch contents and step contents; it is not a new model holdout or a training-quality study.

## One merged execution Goal

| Gate | Work | Continuation rule |
| --- | --- | --- |
| A, CPU only | Read node164 R26 raw OOM/PASS receipts, log steps, common checkpoint and 207-item manifest by hash. | Missing or contradictory primary evidence: STOP before new GPU work. |
| B, prepare/qualify | Verify one exact 6,357,543-byte train parquet and tokenizer; freeze the varied CPU bank; migrate exact R26 common CPU state; adapt scoped component; B1 four-step B0/C1/S2 numerical and checkpoint qualification. | Source/input or numerical failure: STOP. Ordinary engineering fixes only before source freeze. |
| C, capacity | Freeze source/bank/classifier, run one bounded B1..128 natural-OOM bracket from B64, then 3/3 adjacent endpoint and same-B witness confirmations. | Unstable/unknown result: STOP. Equal, regressed or censored result: report and STOP without stretching the claim. |
| D, positive only | At B_common, one-step numerical and 32-step C1/S2 comparison plus fresh-process recovery; at the S2-only witness, 32-step finite/identity/memory and recovery. | Any long-horizon failure: retain five-step result only and STOP; no retune or alternate B. |
| Close | Limited diagnostic allocator pair only if positive and attribution unresolved; publish code, raw hashes, review pack and STOP. | No production pilot or automatic next stage. |

This merges evidence audit, component changes, data authority, capacity and trajectory into one Codex execution branch. It avoids another formal timing campaign: the scientific decision is feasibility under varied data, not small nominal median differences. The capacity classifier must be generic; report generation may not hardcode observed endpoints.

## Decision after the result

- Positive requires same-B C1 OOM 3/3 versus S2 five-step PASS 3/3 **and** S2 32-step witness/resume success, common-B numerical/trajectory checks, correct bank/state identity and clean resource closure. Claim stays limited to this model, input stream and training scope.
- Negative or unstable closes R27. C1 remains default; S2 remains only an explicit capacity option where previously qualified.
- A positive R27 could justify a **separate** small production-quality integration decision. It does not authorize changing defaults, arbitrary autograd/all-parameter training, deployment, hardware/PPA or node174/Accel-Sim.

Shared GPU lock: `/data/c16/locks/c16_gpu_campaign.lock`. Only Lane G/node109 is authorized for this Goal; node164 stores durable raw/checkpoints. No execution is implied by this handoff publication.
