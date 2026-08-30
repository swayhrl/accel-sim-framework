# ADR-009 — Motivation WBUF Shadow Definition

Status: **ACCEPTED**

## Context

The calibrated EP-L2 simulator does not contain an independent finite hardware writeback-data buffer whose capacity can directly be called `WBUF=4/8/16`. Dirty eviction creates a lower writeback transaction while WAD independently tracks line-address ordering/hazards through later completion.

For the motivation blocking-breakdown figure, the study needs a physically meaningful finite writeback-data staging resource without changing the accepted baseline timing.

## Decision

Define a timing-neutral shadow **Dirty Writeback Data Buffer (WBUF)** as follows.

### Meaning

One WBUF slot represents one complete 128-B dirty-line data / WB packet after victim payload readout and writeback-packet creation, waiting for the lower path to accept the WB.

### Allocation

Allocate at the real production event that creates the lower writeback packet after the required dirty-victim data readout.

### Release

**Release when the real writeback packet is successfully accepted into the per-slice lower path / L2->DRAM interface.**

Do not hold the WBUF slot until final WB completion / `set_done()`.

### Relationship to WAD

WBUF and WAD are different resources:

```text
WBUF = dirty data / packet staging before lower acceptance
WAD  = line-address ordering/hazard state across the longer WB lifetime
```

WAD may remain allocated after the WBUF slot has been released.

### Capacities

Evaluate capacities 4, 8 and 16 simultaneously in one timing-neutral execution using the same observed request/WB stream.

The resulting values are `trace_projected` / `would_block` pressure, not three counterfactual timing simulations and not direct performance results.

## Consequences

- Motivation data for WBUF=4/8/16 do not require three workload replays.
- A later functional architecture that actually instantiates WBUF=C must be simulated separately for performance.
- WB-path blocking figures may combine WAD/order restrictions with the shadow WBUF capacity restriction, but must label the category `WB-path` or `WBUF(proxy)` rather than claim the original simulator had a dedicated WBUF.
- The implementation must provide a source map proving the exact creation and lower-accept release events.
