# Lane B — Immediate D512 Preflight Promotion Evaluation

Date: 2026-08-30

Purpose: unblock Lane C/E as soon as the **Banked D512 scan** preflight row is locally complete. Do not wait for the remaining Legacy scan or 3mm mirror rows if they are not required by B6.

## Existing reviewed state

Already accepted by ChatGPT:

```text
D256 backward equivalence: PASS
D512 source/config/cardinality generalization: PASS
>256 natural telemetry: PASS
Banked vectorAdd_4M: COMPLETE_VALID
Banked spmv: COMPLETE_VALID
Banked FWT_7_21: COMPLETE_VALID
Banked sad low-pressure control: COMPLETE_VALID
Legacy vectorAdd paired control: COMPLETE_VALID
```

Frozen D512 candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
runtime config composite SHA-256
a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
```

The only previously missing B6 workload was Banked `scan`.

## Execute now

If the frozen Banked D512 `scan` row has completed, validate it immediately without waiting for Legacy scan or either 3mm row.

Require:

```text
COMPLETE_VALID
normal exit
exact frozen Core/Framework/config/trace identity
terminal_clean = 1
payload consistency = 1
parser success
required C7e telemetry present
Descriptor pool = 512
Line MSHR = 128
per-address cap = 32
no unauthorized config delta
no producer/invariant defect
```

Report its D256->D512 values for at least:

```text
cycles
descriptor need/block/avg/p95/max
Line-MSHR avg/p95/max/full-block
per-address-cap
L1 pressure
WAD/payload/bank
L2->DRAM/scheduler
native DRAM bus utilization using approved Lane-D V3 semantics where available
5K temporal behavior
```

## Promotion decision

If Banked scan and all previously completed preflight rows satisfy B6, publish immediately:

```text
D512_PREFLIGHT_PASS
D512_READY
```

for the exact frozen candidate above.

Do **not** wait for full 26/26 mirror completion to publish `D512_READY`.

Then:

1. update `PARALLEL_WORKBOARD.md`:
   - `D512-PREFLIGHT = DONE`
   - review/evidence path unchanged for ChatGPT to assess
   - keep `D512-MIRROR = RUNNING` if Legacy scan/3mm remain live;
2. publish a machine-readable preflight gate record with exact candidate/config identity;
3. correct the previously reviewed convolution Line-MSHR finding in the Lane-B final/interim analysis metadata;
4. correct the D256 scan-equivalence gate metadata so that the D256 equivalence gate does not depend on itself or on D512 preflight;
5. notify Lane C/E through the workboard that their exact matching D512 descendants are eligible for promotion without rerun.

If Banked scan fails any B6 criterion, publish `D512_PREFLIGHT_FAIL` with the exact reason and do **not** promote descendants.

## Mirror continuation

Regardless of preflight promotion, leave any still-running Legacy scan/3mm mirror jobs untouched. `D512_MIRROR_COMPLETE` still requires all 26 rows to finish and pass final promotion/provenance closeout.
