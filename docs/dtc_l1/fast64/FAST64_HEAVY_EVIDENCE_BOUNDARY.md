# DTC FAST64 Heavy-Evidence Boundary

Status: **ACTIVE — HEAVY M5 EVIDENCE PRESERVED, NOT PRIMARY-GATING**

## 1. Purpose

This file prevents two opposite errors:

1. discarding expensive existing M5 evidence merely because FAST64 becomes the
   primary performance path;
2. allowing expensive heavy payloads to continue blocking FAST64 even though
   their mechanism-validation role is already covered elsewhere.

## 2. Preserved heavy evidence

### BICG repaired-Core M5 evidence

Disposition: `MECHANISM_FIDELITY_ANCHOR`.

Keep as a high-confidence trace-path and Base/IO/OO accounting anchor.

### SpMV repaired-Core M5 evidence

Disposition: `MECHANISM_FIDELITY_ANCHOR / HEAVY_IRREGULAR_SUPPORT`.

Keep its exact capture/immutable/replay evidence where already valid.

### Large 80-SM ATAX Base/IO/OO

Disposition: `BACKGROUND_HEAVY_REPAIR_STRESS`.

If the existing healthy triplet remains affordable, allow it to finish in the
background. It is no longer a FAST64 gate after FAST64.2 passes. Do not launch
new duplicate large ATAX rows solely to qualify FAST64.

### SYR2K

Disposition: `DEFERRED_HEAVY_AUXILIARY`.

Preserve existing capture/archive/immutable evidence. Do not require new
primary-path replay or sensitivity work. Resume only for a separately justified
auxiliary question or when storage/runtime cost is no longer problematic.

### 2MM

Disposition: `DEFERRED_HEAVY_AUXILIARY`.

Preserve the validated compressed archive and its SHA evidence. Do not require
large local unpack/immutable receipt for FAST64 completion. Do not recapture.
Resume the original receipt path only when sufficient storage is intentionally
provided and the auxiliary value justifies the cost.

## 3. Artifact-retention rule

This pivot does not authorize deletion of existing scientific artifacts.

Any later space-reclamation action requires a separate proof that:

- a durable compressed/archive copy exists;
- its SHA is verified;
- required provenance/receipts are retained;
- the deleted object is redundant/regenerable;
- no currently accepted result depends on an unrecorded local path.

## 4. Reporting use

Tier-C heavy results may appear in appendices, robustness discussions, or
mechanism-validation sections, but they must use their original platform and
payload identities.

Do not mix them numerically into `GM-FAST12`.

## 5. Extended-20

Existing Extended-20 E1 work is preserved as `DEFERRED_OPTIONAL_GENERALIZATION`.
It is not a FAST64 completion gate. After FAST64.4/5, selected additional
workloads may be revisited only under a separately documented extension rule;
FAST12 membership remains unchanged.
