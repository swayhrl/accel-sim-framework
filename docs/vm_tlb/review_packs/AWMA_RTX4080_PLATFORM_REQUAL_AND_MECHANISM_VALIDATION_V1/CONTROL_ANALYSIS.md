# Exact contextual control analysis

Scope: `RTX4080_ADA_BASE_V1 + AWMA_MODEL_RELATIVE_VM`.

Legacy 10/80 measurement medians (cycles/dependent step): M0=64.322266, M1=144.554688, M2=1307.904297, M3=160.239258.

- simulator M1/M0: `2.247350682`; Native: `5.653846154`
- simulator M2/M1: `9.047816570`; Native: `0.952380952`
- simulator M3/M0: `2.491194243`; Native: `2.932692308`

M0-M3 remain mechanism-inactive controls. The matrix is for relative/contextual behavior, not hardware TLB latency or capacity fitting. No parameter was changed from these results.
