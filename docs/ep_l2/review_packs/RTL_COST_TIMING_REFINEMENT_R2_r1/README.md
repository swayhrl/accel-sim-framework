# EP-L2 RTL R2 bounded refinement

Actual finite full-capacity controller/access cut; all three modes have unclosed timing.
No whole-L2 area/Fmax, target-GPU PPA or current-SIM-performance coupling.

|Mode|R1 area|R2 area|Change|R1 WNS ns|R2 WNS ns|R2 WNS2ns|
|---|---:|---:|---:|---:|---:|---:|
|B16|2069971.036|1598557.058|-22.774%|-13.614565|-1.413025|-0.296418|
|S64|2121045.696|1627498.656|-23.269%|-13.612103|-1.400875|-0.284268|
|UNIFIED|2525345.746|2432606.442|-3.672%|-36.605915|-1.700971|-0.584364|

All areas are actual Nangate typical1.1V25C Liberty reference units. Same library
hash2efd0b32, SDCde89d1bd, fast-clean ABC883ps, IO/load/PVT/units/widths and
GEN32/full1024/1168/128/4x292/P1. No false/multicycle/reset exception.2ns is a
separate STA of the same mapped netlist. Both raw and normalized mapped netlists
are included as lossless gzip; original and archive hashes are indexed.

Balanced per-bank first-free,16-word metadata/Tag-map distribution, parallel-prefix increment
and real charged reset buffer trees plus proven static hardwires preserve capacity/service
and lifecycle events. The exact R1 base terminal counts AND cycles match for all
three modes; Unified last slot/bank3 drain also matches. This is bounded functional
evidence, not global/post-map equivalence or whole-app numerical proof.

R1 is immutable. Its known pin old-red artifact is reused, not rerun. New-green pin
cases run against R2. Lane3 numeric10cases/13snapshot-read+10final-lines per mode
consume actual RTL output. Abstract observe strings are covered separately by the
base fixture; they are not automatically proved by the byte reference. Metadata
word induction has explicit static-input restrictions; read WORD_EQ_SCOPE_R2.

Full helper first-free SAT covers every binary mask at292/128/16/64. Full1168x32
read mux SAT passed after an appropriately admitted8GiB phase; the2GiB stop and
the shared-monitor false output stop are preserved. The corrected optional proof
monitors only its own output directory; global12GiB/floors never changed.

Read the actual primary critical paths, module cost breakdown, and additional
register/control paths. Additional path filters retain exact primary WNS/TNS and
keep reset timed; no path exception improves the table. Residual high fanout, metadata
and interface timing/DRC remain; no physical buffer/CTS/layout closure is claimed.

SRAM four292x1024 1RW/128byte-enable boundaries total146KiB; actual macro area/delay
remain UNKNOWN, not DFF data-array estimates. Native full-address Tag/LRU/dirty-byte
MSHR/NoC/lower queues remain external UNKNOWN costs. Control metadata and1024-bit
copy/request/response/WB holding registers are actually standard-cell charged.

SIM/RTL frontend II4/II3, static copy, return/arbitration/native approval differences
from R1 remain. No R2 cycle/register stage was added; no official simulator patch or
Lane5 app was launched. A later timing model needs Lane1 review after real buffering,
macro binding and throughput matching. No blanket extra hit cycle is authorized.

DC entrance rtl/ep_l2/flow/run_dc_r2.sh uses same RTL/filelist/common SDC and explicit
actual DB/PVT/operating condition/units/drive/load. dc_shell absent: DC UNRUN. Power
and post-layout UNRUN. See DC_HANDOFF_R2; no made-up target library or macro result.

Resources: central leases; own cap stays12GiB despite a later shared16GiB policy;
workspace48GiB/Share40GiB/availableRAM64GiB/global CPU and memory protections remain.
All R1 reports/netlists/tests and old review packs preserved; only own new R2 copies
were losslessly archived. No other project process/data/quota changed.

Local canonical artifact root: /workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2_v3
Source canonical RTL: f54d3c054a6a03c85b40a1c5018751958c78a129
Read RTL_COST_R2_RECEIPT.json and attached evidence; unpublished/premature attempts
are retained engineering history, not additional accepted performance evidence.

Equal optimization strengthens the static baselines. In this same partial cut,
Unified/B16 reference area is 1.521751x (R1 1.219991x).
Unified/S64 reference area is 1.494690x (R1 1.190614x).
This larger relative dynamic-control overhead must be reported with the absolute
reductions. It does not establish whole-L2 overhead or net application benefit.
