# R3A actual measured attribution and next port constraints

Frozen actual five-file source ac607192957cfd2d69d76bfbc73531b5dbe57523.
R2 frozen1b011c6a5. All areas are reference standard-cell controller/access
cut only; SRAM/native costs UNKNOWN, no whole-L2/app pairing.

|Mode|R3A area|Change vsR2|FF|WNS0.883392226ns|TNS(ns)|WNS2ns|
|---|---:|---:|---:|---:|---:|---:|
|B16|1437416.652|-10.080%|88685|-1.370226|-89682.976562|-0.253619|
|S64|1478834.714|-9.135%|90833|-1.393728|-93801.960938|-0.277121|
|UNIFIED|1847603.016|-24.048%|121550|-1.447954|-154728.968750|-0.331347|

|Mode/module|R2 area|R3A area|Delta|R3A FF|
|---|---:|---:|---:|---:|
|B16/ep_l2_metadata_word|670932.864|503616.736|-167316.128|52768|
|B16/ep_l2_tag_map_word|0.000|0.000|0.000|0|
|B16/ep_l2_generation_step|0.000|0.000|0.000|0|
|B16/ep_l2_index_mux|483216.930|483216.930|-0.000|0|
|B16/top_or_other|443292.990|449468.712|6175.722|35909|
|S64/ep_l2_metadata_word|690697.728|515810.176|-174887.552|54400|
|S64/ep_l2_tag_map_word|0.000|0.000|0.000|0|
|S64/ep_l2_generation_step|0.000|0.000|0.000|0|
|S64/ep_l2_index_mux|483216.930|483216.930|-0.000|0|
|S64/top_or_other|452455.892|478679.502|26223.610|36425|
|UNIFIED/ep_l2_metadata_word|1362056.192|692212.864|-669843.328|73584|
|UNIFIED/ep_l2_tag_map_word|0.000|0.000|0.000|0|
|UNIFIED/ep_l2_generation_step|0.000|0.000|0.000|0|
|UNIFIED/ep_l2_index_mux|483216.930|483216.930|-0.000|0|
|UNIFIED/top_or_other|583352.630|668192.532|84839.902|47958|

U−B16 area834049.384 →410186.364; U/B1.5217514 →1.2853636;
U/S641.4946903 →1.2493641. ALL GEN32/other FF counts remain unchanged.
The reduction is actual combinational compute/control restructuring; the
metadata savings are partly offset by charged shared distribution/lookup logic.
All three clocks remain unclosed, including2ns. No targetGPU Fmax is inferred.

## Real ports, not source-instance counts

R2 has19 explicit source mux instances, but GEN head/active/free-staging
observations are assertion-only after SYNTHESIS (WAD_payload_gen is debug-only).
Actual functional GEN reads are old/admission,p_landing,fill,pin,p_old: five.
R3A merges transaction p_landing/p_old/free-staging selection by use phase,
but lower now needs a REAL read to feed its shared increment. Actual functional
GEN reads are old,transaction,fill,pin,active: still five. The source instance
count reduction19→17 must not be reported as two saved physical GEN read ports.
Area accounting includes that newly functional lower port and data routing.

Two true GEN write intents remain: frontend and lower. Their targets may be
different rows of the SAME bank; P1 limits data grants, not metadata writes.
B0 production owner fixture actually exercised this same-bank pair in all
modes before resource stop. Exhaustive GEN3/32 port miters include same-slot
lower priority. No single1RW metadata macro satisfies the stated ports.

Potential next work, NOT implemented/measured: bank-local GEN compute could
use two writers per each of four banks (up to8 small engines) and local292-row
read paths. One engine per bank would violate simultaneous FE/lower updates.
Any extra pipeline requires a distinct candidate/latency disclosure and Lane1
review. It cannot be inferred as a fixed extra GPU hit cycle from these WNS.

Resident-sector Tag organization retains independent req/fill reads and
frontend/fill field writes. External pin has PID+GEN and no Tag; pin-by-Tag
needs a paid inverse lookup or retained per-payload pins. B final removes only
reverse fill owner; it retains those pin/sector arrays and charges the forward
Tag-map read. No unimplemented SRAM is assigned zero area or timing.

## Actual primary path excerpts (all reset paths remain timed)

B16:
Startpoint: fill_pid[1] (input port clocked by slice_clk)
Endpoint: _678464_ (rising edge-triggered flip-flop clocked by slice_clk)
                                              2.175176   data arrival time
                                             -2.175176   data arrival time
                                             -1.370226   slack (VIOLATED)

S64:
Startpoint: _720031_ (rising edge-triggered flip-flop clocked by slice_clk)
Endpoint: _720063_ (rising edge-triggered flip-flop clocked by slice_clk)
                                              2.198871   data arrival time
                                             -2.198871   data arrival time
                                             -1.393728   slack (VIOLATED)

UNIFIED:
Startpoint: _875839_ (rising edge-triggered flip-flop clocked by slice_clk)
Endpoint: _875861_ (rising edge-triggered flip-flop clocked by slice_clk)
                                              2.253088   data arrival time
                                             -2.253088   data arrival time
                                             -1.447954   slack (VIOLATED)

R3A base4/Lane3three/concurrencythree passed; the full-bank3 terminal test was
resource-interrupted and is NOT PASS. These true mapping/STA numbers do not
qualify a complete new release until that mandatory actual test finishes.
