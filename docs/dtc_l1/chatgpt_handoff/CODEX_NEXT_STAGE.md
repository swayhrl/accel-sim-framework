# CODEX_NEXT_STAGE

## Status

**SIMULATOR SG3 CLOSED — NO NEW SIMULATION AUTHORIZED**

The accepted SG3 downstream-localization authority is:

`6886930ab22d63701e58732cfde18ba019d1dfde`

All A-H, R3, R4, and R5 evidence is frozen.

## Objective

Do not launch further SG3/downstream simulator experiments.

The next project phase is paper-facing synthesis and hardware-cost evidence.

## Required read order

Before any next task:

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md`
3. this file
4. accepted review packs:
   - `FAST64_FINAL`
   - `DOWNSTREAM_HEADROOM_V1`
   - `MEMORY_QUEUE_CHAIN_DRAM_HEADROOM_V1`
   - `ICNT_L2_INGRESS_HEADROOM_V1`

## Authorized work without new scientific review

Codex may perform only non-simulator synthesis/support work, such as:

- assemble paper-facing summary tables from accepted evidence;
- produce figure-ready TSV/CSV from accepted rows;
- trace each paper claim to its accepted review-pack evidence;
- clean up wording/labels so cycle reduction, speedup, and counter semantics are unambiguous;
- prepare RTL/DC experiment inputs/scripts that do not alter the accepted simulator evidence;
- draft/update paper-support documentation requested by ChatGPT.

No new numerical simulator row is authorized.

## Important reporting cleanup

When reporting R5 and other comparisons:

- distinguish **cycle change** from **speedup/performance change**;
- e.g. G/IO has cycles lower by about 0.16%, whereas G/OO has cycles higher by about 1.71%;
- avoid a column named “delta” unless its sign convention is explicitly defined.

Legacy counter text `gpu_stall_dramfull` must be described by its source semantics as `gpu_stall_icnt2mem` ingress-admission pressure.

## Explicitly forbidden until a new ChatGPT handoff

Do not launch:

- any SG3 queue/NoC/ROP/DRAM experiment;
- any new DTC-cap point;
- any new L2 capacity/MSHR/logical-Tag point;
- FAST12 sensitivity expansion;
- GESUMMV extension of R5;
- any architecture mechanism added only to chase SG3 results.

## STOP boundary

If asked to continue without a newer handoff, perform only paper/RTL support work and do not start simulation.

A new simulator stage requires explicit ChatGPT authorization based on a new scientific question.
