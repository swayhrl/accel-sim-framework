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
masked write, so a Snapshot bit-set is a two-cycle read-modify-write; query
reads issue to all four replicas in parallel. This is functionally correct
and explicitly backpressures the update interface. It is lower throughput
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

The reproducible 1ns macro-aware CTS run after this change is
`results/openroad_c2p_asap7_sram_bf_2cycle_nonlinear_cts_1ns`. Its WNS is -947.9597ps;
the reported worst path is no longer in a BF engine. It is the 1RW adapter's
read-modify-write path from `g_bank_3__copy3/dataout[17]` through two small
logic cones to `g_bank_0__copy3/wd[17]`. The two BF engines map to 145.63962
and 88.60266 um2 respectively, and total non-SRAM standard-cell logic is
1,276.97472 um2. This confirms removal of the hash-to-`banksel` critical
cone, but it is not a 1ns-clean total design: the public single-port macro
decomposition and its cross-macro RMW wiring need a multiport/masked-write
Snapshot macro or a different bank-local update microarchitecture.

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
exactly; the implementation does not yet match the paper's 128-engine
parallelism or complete non-SRAM control scope. The next RTL step is a
128-engine dispatcher plus 64-bank/four-copy address arbitration (the
single-engine pipeline is now the verified building block), followed by a
routeable macro view for the final physical run.
