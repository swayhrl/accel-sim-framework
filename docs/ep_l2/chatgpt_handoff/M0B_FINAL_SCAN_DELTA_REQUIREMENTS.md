# EP-L2 M0b — Final Scan Delta Requirements

Status: **incremental closeout only**.

The 9-of-10 source/semantics/mechanism-direction review is already complete. When the existing `scan` ON process finishes naturally, do not rerun any completed row.

## Required final delta

1. Verify scan used the same frozen M0b Core/runtime config/trace family.
2. Parse the existing scan output with the same strict parser and 64-slice cardinality gate.
3. Add scan to RO candidate/lifetime and production payload-role aggregates.
4. Check whether scan contains dirty victims and, if so, whether any old resident payload handle remains live after reassignment.
5. Check whether scan creates any real production non-resident payload allocation.
6. Refresh the final opportunity matrix.
7. Run final read-only OFF/ON equality summary for the three controls; do not create a scan OFF pair unless already prescribed elsewhere.
8. For deterministic parsed artifact equality, compare every artifact family emitted by both OFF and ON runners. Explicitly mark non-emitted families rather than omitting them silently.
9. Preserve the explicit scope note:

```text
FWT_7_21 = WAIVED_AS_REDUNDANT_FOR_CURRENT_TVD_PAYLOAD_HANDLE_PREMISE
```

This waiver applies only to the already-falsified old-resident-payload-hold TVD premise, not to future WAD studies.

## Final review trigger

Publish the final `M0B_OPPORTUNITY_r1` and updated `LANE_M0B_LATEST.md` with status:

```text
M0B_OPPORTUNITY_LOCAL_COMPLETE
```

Then request only a small ChatGPT delta review. Do not reopen source/producer review unless scan reveals a source/config/semantic mismatch.
