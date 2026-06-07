# Updated LATPC reproduction plan after A19

## Completed

A16: LATPC paper-specific baseline vs no-op variant slot.

A17-A18: LATPC paper requirements, code localization, and print-only stats plumbing.

A19: VM/TLB/PTW/PWC foundation assessment. Result: current tree has address observation and stats print path, but no complete active L1/L2 TLB, TLB MSHR, PTW, page-walk queue, or PWC foundation was localized.

## Current large round

A20-A23: Build a shadow VM/TLB/PTW/PWC substrate.

Purpose:

- create a side model that observes addresses and derives VPNs
- provide non-trivial TLB/MSHR/PTW statistics
- keep simulator timing and control behavior unchanged
- make future LATPC mechanism analysis possible

This round does not reproduce LATPC speedup.

## Planned next rounds after A20-A23

### A24: Regularity Detector over shadow VM substrate

Goal:

- consume shadow unique VPN streams
- compute VPN, Stride, Index metadata
- preserve lane order
- detect stride groups
- compute prefetch candidate translations
- generate Figure 3, Figure 8, and Figure 9 style stats

No real prefetch injection yet.

### A25: LATC over shadow MSHR

Goal:

- implement shadow LATC compressed MSHR behavior
- add Base VPN, 9-bit Stride, and 32-bit Valid Mask in the shadow model
- compare baseline shadow MSHR vs LATC shadow MSHR
- measure reservation failure reduction

No real TLB MSHR behavior change yet.

### A26: LATP over shadow PTW

Goal:

- implement shadow LATP batching and L4 page table locality model
- reduce shadow PTW requests or shadow queue stall
- compute coverage and accuracy style stats

No real PTW batching yet.

### A27: Combined LATPC shadow analysis

Goal:

- combine Regularity Detector, shadow LATC, and shadow LATP
- run baseline shadow, LATC shadow, LATP shadow, and LATPC shadow
- produce NW single-workload mechanism-potential report

This still cannot claim IPC speedup reproduction unless timing integration is implemented.

### A28: Timing VM integration design

Goal:

- design how to make translation latency affect simulator timing
- define L1/L2 TLB latency, PTW latency, MSHR blocking, replay behavior
- keep disabled baseline identical
- identify targeted validation cases

### A29: Minimal timing VM foundation

Goal:

- implement timing-affecting baseline VM translation model
- validate disabled baseline
- validate enabled timing VM on targeted cases
- do not add LATPC mechanisms yet

### A30: Timing Regularity Detector, LATC, and LATP integration

Goal:

- port A24-A26 shadow mechanisms into the timing VM foundation
- run baseline, LATC, LATP, LATPC timing variants
- validate no deadlock and correct release behavior

### A31: Targeted validation suite

Goal:

- synthetic or small targeted cases for page divergence, stride, same-L4 locality, MSHR full, PTW queue pressure
- validate corner cases before paper-style benchmark runs

### A32: NW paper-style result

Goal:

- run NW baseline, LATC, LATP, LATPC
- report IPC or timing proxy, translation latency, PTW stall, MSHR fail, coverage, accuracy
- compare trends with LATPC paper

### A33: 4-8 workload expansion

Goal:

- expand to trace-available LATPC paper workloads
- priority: nw, lud, backprop, bfs, and any available Polybench workloads
- include Regular+Low, Regular+High, and Irregular if possible

### A34: Figure and table alignment

Goal:

- generate paper-style CSVs and plots for:
  - page divergence
  - unique VPN strides
  - same L4 PT locality
  - IPC or timing proxy
  - translation latency
  - PTW stall
  - MSHR reservation failure
  - coverage and accuracy

### A35: Workload coverage gap analysis

Goal:

- build canonical 24-workload LATPC table
- map local trace availability
- document blocked workloads
- separate bounded reproduction from full-paper reproduction

### A36: Optional prior approaches

Goal:

- implement or approximate Sequential, Stride, Distance prefetchers first
- defer Valkyrie and Avatar unless needed
- clearly distinguish LATPC-vs-baseline reproduction from full Figure 17 reproduction

### A37: Bounded reproduction closeout

Goal:

- produce final bounded reproduction package
- include code, configs, CSVs, figures, known limitations, and review pack

If timing integration is complete and multiple workloads are covered, this can be called bounded LATPC mechanism reproduction.

If only shadow modeling is complete, call it bounded LATPC shadow-mechanism analysis.

## Full paper reproduction beyond A37

Full paper reproduction would require:

- as many of the 24 workloads as possible
- timing-affecting VM/LATPC model
- 2 MB page sensitivity
- TLB/PTW sensitivity
- prior approach comparison if claiming full Figure 17 coverage
- final reproducibility package
