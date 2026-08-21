# C2P Snapshot SRAM — open ASAP7 integration result

This is a reproducible **macro-aware RTL implementation experiment**, not a
sign-off PPA claim. It records both the useful evidence from the public ASAP7
SRAM views and the condition that prevents a DRC-clean total result.

## Implemented geometry

The C2P-Cache paper's default Snapshot Matrix is 5,120 rows by 64 bits, with
four physical copies. The integration uses the pinned `asap7_sram_0p0`
revision `9f5af0939e8dd3cc1a9693a50b23441691dd7d25` and its
`srambank_256x4x64_6t122` macro.

| Item | This RTL integration | Paper default |
| --- | ---: | ---: |
| Logical Snapshot | 5,120 x 64 | 5,120 x 64 |
| Physical copies | 4 | 4 |
| Physical capacity | 160 KiB | 160 KiB |
| Macro decomposition | 20 x 1,024 x 64 | 64 banks x 4 copies |
| Macro area | 20 x 2,359.86048 = 47,197.2096 um2 | CACTI scaled: 0.0804 mm2 |

Five 1RW macros compose a logical 5,120x64 replica. The public macro lacks
masked write, so a Snapshot bit-set is a read/capture/write transaction; query
reads issue to all four replicas in parallel. The capture register removes the
macro-Q-to-macro-D path, and query admission is ordered behind accepted
updates. This is functionally correct and explicitly backpressures the update
interface. It is lower throughput
than the paper's 64-bank, four-copy high-concurrency organization, which
provisions 256 row reads/cycle and 128 BF engines.

## Functional and implementation checks

```bash
C2P_IVERILOG_BIN=/scratch/root/oss-eda/oss-cad-suite/bin/iverilog \
C2P_ASAP7_SRAM_ROOT=/tmp/c2p-asap7-sram \
tools/c2p_ppa/run_c2p_rtl_test.sh /tmp/c2p-rtl-asap7
```

All three forms pass the same directed C2P scenarios: reference storage,
generic masked 1R1W test macro, and the upstream behavioural ASAP7 macro.
The test covers candidate ordering, exact-miss continuation, remote hit,
no-candidate fallback, requester self-exclusion, and deterministic tie break.

With the pinned OpenROAD build `fd4b90e86cfdb5059c9e6dbeeba3202cc3cb5e48`,
the synth check instantiates exactly twenty SRAM masters. Macro-aware
floorplanning places all twenty macros in fixed five-by-four coordinates,
connects their VDD/VSS pins through the ASAP7 PDN, and creates a
89,583.807 um2 core. At an exploratory 8ns constraint, the post-CTS path has
+922.6864ps slack. This deliberately relaxed point establishes that the views
can participate in placement/PDN/CTS; it is not the paper's 1.41GHz model
point.

The historical unpipelined implementation had a 1ns pre-CTS WNS of
-5,994.1846ps, on full-width `fold_hash` arithmetic through Snapshot address
decode into macro `banksel`. The current RTL replaces that reference-only hash
with two explicit, elastic, two-cycle `c2p_bf_engine` instances (one each for
updates and queries). Their folded 12-bit hardware hash has no full-width
multiplier and is checked row-for-row against its defined mapping. Therefore
a registered BF result—not raw request data—drives each Snapshot address.

The paper assumes a two-cycle BF engine and a two-cycle Snapshot lookup. The
new engine matches that latency budget and preserves C2P correctness because
every candidate still receives an exact remote-L1 probe. It intentionally does
not reproduce the simulator's splitmix false-positive distribution, so any
candidate-rate comparison must use the matching hardware hash in the model.

The current reproducible 1ns macro-aware CTS run is
`results/openroad_c2p_asap7_sram_cluster_capture_ordered_cts_1ns`. Its WNS is
**-512.0120ps**. The reported worst path is no longer in a BF engine nor
directly from a macro output: it starts at the registered RMW capture data and
ends at a selected macro `wd` input. This confirms removal of the
hash-to-`banksel` and macro-Q-to-macro-D critical cones, but it is not a
1ns-clean total design: the public single-port five-macro decomposition still
places a wide, high-fanout RMW write net on the timing boundary. A
multiport/masked-write Snapshot macro or a bank-local update microarchitecture
is required for a closing macro-aware implementation.

The scalable control front end is separately synthesized as
`results/openroad_c2p_banked_frontend_two_cut_fabric_synth`. It
instantiates 128 two-cycle BF engines, four 64-bank request arbiters, four
two-cut owner-routed response fabrics, and the four-copy response joiner.
The default 128-engine arbiter is a static 8-by-16 priority tree (the generic
arbiter remains only for small directed tests), so its elaborated selection
cone has neither a behavioral first-one encoder nor a variable-indexed grant
write. The mapped ASAP7 standard-cell area is **156,008.4057 um2
(0.156008 mm2)**, before target-L1 queues, physical Snapshot macros and
physical-only cells. This result completes in Yosys (141.63s, 806.54MB peak)
and is therefore a reproducible mapping result, not a route/timing signoff.

This number is deliberately reported as a design finding rather than a
success metric: four seven-layer route networks use only two elastic packet
cuts each, rather than buffering both 71-bit paths at every hop. They account
for about 0.0799mm2; the joiner adds 0.016161mm2 and the request-side
hierarchy and BF engines make up the remaining mapped area. This halves the
previous fully registered return-network area and reduces the total front-end
mapping by 33.9%; it also replaces the
previously unmappable flat response crossbar. It is still above the paper's
0.0682mm2 logic estimate before target queues and physical-only cells. A
future closing implementation needs bank-local response reservation with a
lower-storage return network (or a technology-specific interconnect/memory
macro); this RTL makes that remaining cost explicit instead of hiding it in
unsynthesizable routing logic.

An OpenROAD CTS-proxy attempt also records the integration boundary precisely.
At the ordinary 25% proxy utilization, `PPL-0024` rejects the top because its
66,050 exposed internal pins exceed the 40,592 perimeter sites. At the
runner's 8% utilization, OpenROAD accepts all 66,050 pins (71,680 sites),
builds a 1,721.811um square core, inserts the standard-cell PDN/taps and
starts global placement. That sparse raw-interface run was intentionally
stopped during Nesterov placement: it has 2.46M physical instances and treats
bank-array wires as die-crossing IO, so its route/timing would measure an
unphysical wrapper rather than C2P. This is not a failed C2P netlist or a
claimed CTS result. The next P&R top must instantiate the Snapshot banks and
target-L1 queues internally, absorbing these signals before the chip boundary.

## Detailed-route gate

A full OpenROAD attempt reaches macro pin access, but the public macro LEF
emits 402 `DRT-0418` warnings: affected macro terminals have no pins on the
routing grid. The same upstream view set also reports an unknown `coreSite`
and a LEF/Liberty disagreement for `sdel[4:0]`. These are view-integration
defects, not evidence of a C2P RTL connectivity fault.

`run_openroad_c2p_asap7_sram.sh` now fails a full run when any `DRT-0418`
warning is present. This prevents an OpenROAD exit status from being mistaken
for a routeable, DRC-clean total-C2P layout. A proprietary 12nm SRAM macro,
or a repaired/open macro LEF with valid pin geometry for the selected track
grid, is still required for post-route timing, DRC and RCX.

## Paper comparison

The paper's Table 3 reports a CACTI 32nm SRAM estimate scaled to 7nm of
0.0804 mm2, 0.0682 mm2 of non-SRAM logic (667,980 cells), OpenROAD placement
of 0.0691/0.0837 mm2, and 0.149 mm2 total. This integration's raw macro cell
area is 0.047197 mm2 and its mapped **single-lane** standard-cell logic is
0.001277 mm2 before physical-only cells. Those numbers must not be added or
compared as total overhead: the paper includes 128 BF engines and
high-concurrency queues/arbitration, while this RTL instantiates one query
lane and uses a different open macro library. CACTI scaling and an ASAP7
macro abstract are also not a common area methodology.

The valid comparison is therefore: geometry and four-copy capacity match
exactly; the implementation now has the paper-shaped 128-engine/64-bank
request front end, registered packet return fabric, and owner-tagged four-copy
response joiner, but still lacks its target-L1 request queues in the single-lane cache top. The open macro view
also remains unrouteable, so it cannot produce a signoff total. The next
physical step is a routeable macro view plus a bank-local/masked update path;
the next functional scaling step is connecting the existing completed
request/response contract to target-L1 queues.
