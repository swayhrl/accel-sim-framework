# EP-L2 R3 final — actual qualified finite RTL and measured cost

Selected actual five-RTL hardware e8d67d13b5205cdcda4c2c750a34f7cda6b0103b;
source release hrl/ep-l2-rtl-r3b-owner-cost-v1 / original execution branch
hrl/ep-l2-ft20261016-lane2-v1 at this enclosing publication commit. Retained
A ac607192957cfd2d69d76bfbc73531b5dbe57523 remains independently finite-qualified
at frozen source ref b4d825b4. Every R1/R2 pack/worktree and old R3 pack is kept.

Both candidates passed the required FINITE configured actual RTL gates; this
is neither unbounded formal equivalence nor officialSIM/application qualification.
All28 executed accepted VVPs were decoded and exact binary/source/fixture SHA
verified. Base4 each(three full1024/1168/128/GEN32 modes plus separateGEN3),
Lane3 actual ten-vector byte/snapshot3 each(13 observations+10 final lines),
three concurrent GEN reservation/commit/rollback+lower cases per mode, three
same-bank different-row GEN/held-pin/late-fill/rebind/byteWB stress modes each,
and highestPID1167/bank3/row291 fullTag/bank-compatible exhaustion,108other-bank
free slots, byteWB37, exact3379cycles each. Both base and boundary counter/cycle
lines match frozenR2 exactly. Common word/GEN3/32 all-index portSAT and scoped
4Tag/32payload/GEN3,4cycle controller control-state proofs retain explicit
premises. Conditional owner invariant is not global reachability. Byte outputs
excluded from that small miter are independently tested by full-size RTL.

Actual same Nangate typical1.1V/25C, sameSDC/ABCfast-clean/GEN32/physicalcapacity:

|Mode|FinalB reference stdcell area|Change vsR2|FF|WNS0.883392226ns|WNS2ns|
|---|---:|---:|---:|---:|---:|
|B16|1414058.128|-11.5416%|88685|-1.400861|-0.284253|
|S64|1455472.200|-10.5700%|90833|-1.393962|-0.277355|
|Unified|1765551.858|-27.4214%|109870|-1.363639|-0.247031|

U/B1.5217514(R2)→1.2853636(A)→1.2485709(finalB);
U/S641.4946903→1.2493641→1.2130440; U−B834049.384→410186.364→351493.730.
All three modes remain TIMING_UNCLOSED, including2ns. Static B16/S64 WNS are
slightly worse thanA while Unified improves. Full WNS/TNS/DRC/path reports and
metadata/Tag-map/top seq/comb attribution are included, with actual-hierarchy
arc-delay partitions and semantic critical FF endpoints. No loss is suppressed.

These are partial controller/access standard-cell reference costs, not wholeL2
or targetGPU mm2/Fmax/net benefit/power.146KiB SRAM(4x292x1024) is an explicit
uncharacterized external macro, never a default DFF array claimed as SRAM.
TraditionalTag/LRU/MSHR/NoC/queue costs UNKNOWN. No SPEF/CTS/PNR/power/DC run.
All32-bit GEN storage retained; two real concurrent payloadGEN engines share
compute, not lifetime/state. Actual functionalGENreads remain five. Role/pins/
sector/WAD/address/FIFO and1024x11 U Tag-map remain paid. FinalB removes
11680 reverse-owner FF and charges its new forward fill lookup; static B/S
use proved PID==Tag identity without an artificial live/map lookup. Tag-index
pins/sector rewrite STOP: paid inverse and true multiple ports remain required.
No fake SRAM saving or irreducible-area lower bound is claimed.

Current remaining critical paths: B/S fill/control through arbitration into
pending_sector_count[15]; U metadataGEN→free eligibility/priority→GENread→shared
GENstep→another metadataGEN. Arc attribution is not independent per-module WNS
or a conversion to extra GPU cycles. Bank-local compute/reads are future work;
metadata needs two writers even within one P1 data bank. Any changed stage/II
is a separate candidate requiring explicitSIM review, not silently applied.

R2 readII4/writeII3/copy/return/RR-vs-oldest/native-approval gaps remain. Only
valid-qualified native identity data is compared; unconsumed native_gen may
differ under phase read sharing. No new source stage, II, bank grant, capacity,
GEN width, service order, pin/lower_accept/set_done responsibility was changed.
No officialSIM source/binary/performance app or Lane5 workload was modified/run.
Prior TVD/common/structural source commits remain; old TVD3 tests stay
NOT_COMPILED_NOT_RUN and this is not completeTVD.

DC-ready exact entry: rtl/ep_l2/flow/run_dc_r3.sh/.tcl, filelist.f/common.sdc
from this source tree with RTL_REPO pointing to this exact checkout and a fresh
central-admitted DC_OUT. MODE0/1/2 fixes all fullparameters. Actual TARGET_LIBS,
LINK_LIBS, OPERATING_CONDITIONS, PVT_LABEL, LIB_TIME_UNIT_NS, IO_DRIVE_CELL,
OUTPUT_LOAD_LIB_UNITS are required; no library is guessed. Scripts record real
DB/source hashes only when executed. DC unavailable: UNRUN, not DC PASS.

The original6hour bounded contract is met, with first exact checkpoint at39min.
Shared20GiB / independently-owned12GiB direct user authorization is recorded;
original workspace48GiB/Share40GiB/availableRAM64GiB and central CPU/RAM leases
were retained. Earlier disk stops/failed attempts are preserved, never PASS.
Ordinary admission recovered and all accepted remaining runs used it. Scoped
47.5GiB exception was neither authorized nor activated; no resident waiter.
All own EDA leases are released; other projects/processes/data/quota untouched.

The remote pack is lean. Large original mapped/normalized netlists and all
accepted or unfinished executables remain at exact central receipt/manifest
paths, losslessly archived with original+compressedSHA. Small actual reports,
proof source/logs/receipts/tables are in Git. PACK_REPORT_ARCHIVE_INDEX records
large-report gzip copies whose central original bytes are untouched. All6 pairs
of mapped/STA netlists and all28 accepted executables were decoded and verified.
Earlier invalid16payload/PID4 toy proofs (including nominal PASS) remain
INVALID_MODEL; corrected32payload proofs are the only selected ones. Full-byte
8step memory/timeout attempts, initial declaration fix, resource interruptions,
publication ignore-rule/readback corrections are preserved in failure ledger.
