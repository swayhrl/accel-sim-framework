# AWMA Project Charter

## 1. Name and naming policy

Official project name: **AI Workload Memory Analysis** (`AWMA`).

Project scope: real-GPU AI workload memory characterization, simulator-based TLB/cache mechanism evaluation, and evidence-aligned cross-view analysis.

`C16` remains a historical campaign identifier. It originally denoted the multimodel native-characterization campaign and now survives in established paths, run IDs, receipts, scripts, and review packs. Existing `C16` names are compatibility aliases, not the long-term project name.

Do not mass-rename:

- `/data/c16`
- `/root/share/mnt164/huangrulin/c16_ai_workload`
- `util/vm_tlb/c16/`
- existing `C16_*` run IDs/review packs
- existing manifest/receipt paths

New project-level metadata should use:

```text
project_name = AI Workload Memory Analysis
project_slug = awma
legacy_campaign_namespace = C16
```

## 2. Scientific mission

AWMA has three long-lived planes.

### Native Evidence Plane

Measures what a real GPU actually executed or observed:

- model/scenario/phase execution identity;
- kernel/launch census;
- NCU hardware counters;
- NVBit/C16WARP1 address observations;
- page/cache-line/object footprints;
- context/batch/prefill/decode behavior;
- real implementation choices such as attention/quantization backend.

### Simulation Evidence Plane

Evaluates counterfactual architecture mechanisms:

- simulator-compatible trace input;
- TLB/PTW behavior;
- cache behavior;
- queueing/stalls/cycles/IPC;
- controlled mechanism variants such as Segment, Selective, cache policies, walker/TLB geometry, etc.

### Cross-view Plane

Relates Native and Simulation evidence only when the workload/target lineage permits it. It is responsible for:

- native-vs-simulator calibration;
- explaining simulated behavior using real-GPU workload properties;
- selecting representative simulation targets from a larger native corpus;
- mechanism applicability boundaries across models/scenarios.

## 3. Core architectural decision

AWMA is **one project and one catalog**, not two disconnected repositories.

However, Native Evidence and Simulation Evidence are different scientific evidence classes and must never be merged into one undifferentiated metric namespace.

The intended model is:

```text
                 AWMA common identity/catalog
                          |
              +-----------+-----------+
              |                       |
        Native Evidence        Simulation Evidence
        REAL_GPU origin        SIMULATOR origin
              |                       |
              +-----------+-----------+
                          |
                     Cross-view
```

## 4. Long-term node roles

- `109 / RTX4080`: GPU capture/producer.
- `174-new / port 2239`: AWMA analysis, catalog, simulator-analysis owner.
- `164 via /root/share/mnt164`: durable AWMA data/archive root.
- old174 / port 2233: not AWMA owner; may continue unrelated Decouple-L1/L2 work. Historical AWMA assets already copied/referenced as recorded by the inheritance review packs.

## 5. Evidence rule

Real-GPU evidence and simulator evidence may disagree. Neither overwrites the other.

Example:

```text
native.l2_metric = observed hardware evidence
simulation.l2_metric = modeled evidence
calibration.delta = explicit comparison
```

A discrepancy is data, not an error to hide.

## 6. Non-goals

This project rename does not authorize:

- rewriting historical raw data;
- recomputing old scientific status labels;
- fabricating temporal order for MREF-sharded C16WARP1 data;
- turning current C16WARP1 into traceg without a lossless proof;
- moving large raw data solely to improve directory aesthetics;
- forcing every Native workload to have a Simulation counterpart.

A workload may validly remain `simulation_status = NOT_SELECTED`.