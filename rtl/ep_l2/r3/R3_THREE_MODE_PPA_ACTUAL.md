# R3 actual three-mode PPA, required finite qualification complete

Canonical final five-RTL source e8d67d13b5205cdcda4c2c750a34f7cda6b0103b.
Comparison baseline R2 hardwaref54d3c054 / publication1b011c6a5;
A hardwareac607192957cfd2d69d76bfbc73531b5dbe57523. Tables inactual_cost_r1
come from real complete Nangate typical1.1V/25C mappings plus two-periodSTA.
Same actualLibSHA2efd0b32eb580e4e60e72fc0575bb3bc69aac907c91d908442e4ae6d7fe55895,
SDCSHAde89d1bdbeaefbbeeb316bfa00525e18e0c9fc013555796f75cc158a1641cbb2,
fast-cleanABC effort/883ps mapping target, BUF_X1 input drive,5fF output load,
reset paths timed, no false/multicycle exceptions, no pipeline/II change.

|Mode|FinalB area (library reference units)|R2 change|FF|WNS0.883392226ns|TNS(ns)|WNS2ns|
|---|---:|---:|---:|---:|---:|---:|
|B16|1414058.128|-11.5416%|88685|-1.400861|-91259.953125|-0.284253|
|S64|1455472.200|-10.5700%|90833|-1.393962|-93803.179688|-0.277355|
|Unified|1765551.858|-27.4214%|109870|-1.363639|-138773.406250|-0.247031|

U−B834049.384(R2) →410186.364(A) →351493.730(finalB).
U/B1.5217514 →1.2853636 →1.2485709; U/S641.4946903 →1.2493641 →1.2130440.
All three clocks remain unclosed, also at2ns. FinalB static B16 WNS is30.635ps
worse than A, S64 is0.234ps worse, Unified improves84.315ps. No negative point
is removed from the comparison, and no targetGPU Fmax/product area is inferred.

Fixed1024Tags/1168payload/128WAD/GEN32/four292x1024bit banks/P1 throughout.
B16 andS64 keep stronger fixed PID==Tag ownership guards; their FF counts
stay unchanged fromR2/A. Unified removes exactly11680 reverse-owner FF;
GEN32, six-bit pins, sector vectors, role fields and1024x11 Tag-map stay paid.
The actual146KiB payloadSRAM is an uncharacterized macro boundary, not a DFF
array substituted into area. TraditionalTag/LRU/MSHR/NoC/queue costs UNKNOWN.
This partial standard-cell controller/access cut is neither wholeL2 nor a
net-performance/energy result; no officialSIM or Lane5 app was modified/run.

Actual source mechanism attribution:
- Two concurrent GEN writer engines are real shared compute313.880 area, no
  added stage. Word-local GEN32 FF remain. A's actual functionalGENread ports
  stay five: merging transaction phase reads is offset by the new real lower
  GENread. Source mux19→17 is not two saved physicalGENports.
- A→finalB removes the real owner10 read selector23328.998 area inALL modes.
  Static B16/S64 need no new live/map read because fixed PID==Tag is proved.
- Unified metadata word total692212.864 →604909.536 (delta−87303.328;
  sequential−52816.960 from11680FF, combinational−34486.368). Its paid new
  forward map/live/compare and changed top logic add28581.168; net wholecut
  A→B−82051.158. Existing1024 Tag-map word area84439.040/11264FF remains.
- Remaining actualGEN32 selectors are five x74616.458 area; they and control
  fanout/arbiter/sector-count paths remain expensive. Any bank-local replacement
  must retain two metadata writers even within the SAME bank. 1RW SRAM cannot
  stand in for the required concurrent metadata ports at zero cost.

Proof/functional scope: conditional word/map owner invariant, commonGEN3/32
SAT and actual three-mode small32payload4cycle controller cut; full-size base,
Lane3 numeric bytes, concurrent GEN and same-bank/held-pin/late-fill tests.
Both A and finalB now have complete required FINITE configured qualification:
all28 accepted executable/source/fixture identities verified, fullbase3+GEN3,
Lane3three, concurrentGENthree, same-bank/held-pin/late-fillthree and bank3
highestPID1167 each. Base and highest counter/cycle lines matchR2 exactly.
This is not unbounded formal proof or officialSIM/application qualification.

ReadII4/writeII3/copy/return/RR-vs-SIM-oldest/native-approval deltas remain.
Only valid-qualified native handle data is compared; unconsumed native_gen
when !native_commit may differ under read sharing. No accepted cycle changes.
Tag-index pins/sector reorganization stopped because externalPID+GEN pins
need a paid inverse resolution and multiple genuine field ports; no imaginary
metadata macro saving is added. These PPA numbers are not irreducible bounds.

DC source entry run_dc_r3.sh/.tcl +filelist.f/common.sdc require real DB paths,
operation-condition/PVT, actual time units and IO cell/load. DC UNRUN (absent),
power/PNR UNRUN; SRAM characterization and full product timing remain open.
All originalR1/R2/checkpoint evidence retained. Exact large raw/netlist/binary
archives remain centrally with original/archivedSHA. Final qualification and
full raw report delivery will use a new review revision without overwriting
prior packs. Ordinary48/40GiB and64GiBRAM admission remains; no47.5GiB
exception has been approved or activated.
