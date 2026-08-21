# Retained C2P RTL/PPA result

This record is deliberately narrow: it is a reproducible implementation of
the C2P **single query-lane control** RTL, not a claim of a complete GPU-cache
chip or a foundry sign-off result.

## Reproduction

The successful retained run used OpenROAD
`fd4b90e86cfdb5059c9e6dbeeba3202cc3cb5e48`, the ORFS ASAP7 RVT/TT platform,
and the following command from this directory's repository root:

```bash
export LD_LIBRARY_PATH=/tmp/c2p-openroad/deps/lib:/tmp/c2p-openroad/or-tools/lib
export C2P_ORFS_ROOT=/tmp/c2p-openroad/OpenROAD-flow-scripts
export C2P_OPENROAD_BIN=/tmp/c2p-openroad/build-real3/bin/openroad
export C2P_YOSYS_BIN=/scratch/root/oss-eda/oss-cad-suite/bin/yosys
C2P_PPA_RESULT_DIR=tools/c2p_ppa/results/openroad_c2p_query_engine \
C2P_PPA_DROUTE_END_ITER=4 C2P_PPA_REPAIR_SETUP=1 \
tools/c2p_ppa/run_openroad_c2p_query_engine.sh
tools/c2p_ppa/summarize_openroad_result.py \
  tools/c2p_ppa/results/openroad_c2p_query_engine
```

The result directory is ignored because it contains generated Liberty,
netlist, DEF, ODB, and logs.  The command recreates all of them from the
versioned RTL and flow configuration.

## Observed result

At the explicit 1 ns `core_clk` constraint, with no artificial IO delay:

| Check | Result |
| --- | --- |
| Post-CTS WNS | +113.2366 ps |
| Post-route WNS (OpenRCX) | +58.4235 ps |
| Post-route design area | 490 um² at 30% reported utilization |
| Detailed-route DRC entries | 0 |
| Extracted signal nets | 4,542 |

The flow runs floorplanning, tap/endcaps, PDN, tie cells, placement, CTS,
global-route incremental repair, pin access, detailed route, filler, and
OpenRCX extraction.  The post-route reports, DEF, and ODB are written only
after those steps.

## Functional gate

Before taking PPA data, run both the reference-array and external-macro
adapter forms:

```bash
C2P_IVERILOG_BIN=/scratch/root/oss-eda/oss-cad-suite/bin/iverilog \
  tools/c2p_ppa/run_c2p_rtl_test.sh /tmp/c2p-rtl-test
```

The directed test checks candidate ordering, an exact-probe miss followed by
the next candidate, peer hit, no-candidate fallback, requester self-exclusion,
and the C++ lower-SID tiebreak.  It also instantiates a synchronous 1R1W macro
stub under `USE_SRAM_MACRO=1`.

## Scope boundary

The 490 um² number is control only.  The four 5,120x64 Snapshot replicas are
at the technology macro boundary and are not inferred as flip-flops or added
as a CACTI number to this ASAP7 result.  Supplying their Liberty/LEF/GDS,
power, and extraction views is the required next step for total-C2P PPA; see
[`openroad/snapshot_macro_manifest.md`](openroad/snapshot_macro_manifest.md).
The result also uses ASAP7 as an open, reproducible early-PPA platform, not
the project's eventual 12 nm production library or IO timing environment.
