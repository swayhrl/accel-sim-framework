# Route-B Q2 Llama bridge handoff

Q2 is ready for Lane A immediately after Q1 passes.  It is producer
qualification, not a representative selection capture.

Frozen Route-A anchors:

| phase | exact full mangled function | historical selected static index |
| --- | --- | ---: |
| PREFILL | `_ZN2at6native44_GLOBAL__N__50c743a2_11_Indexing_cu_89862edb21indexSelectLargeIndexIN3c104HalfEljLi2ELi2ELin2ELb1EEEvNS_4cuda6detail10TensorInfoIT_T1_EENS7_IKS8_S9_EENS7_IKT0_S9_EEiiS9_S9_l` | 101 |
| DECODE | `_ZN2at6native44_GLOBAL__N__50c743a2_11_Indexing_cu_89862edb21indexSelectSmallIndexIN3c104HalfEljLi2ELi2ELin2EEEvNS_4cuda6detail10TensorInfoIT_T1_EENS7_IKS8_S9_EENS7_IKT0_S9_EEiiS9_l` | 17 |

The historical target receipts are `LARGE_INDEX_PREFILL_TARGET.json`
(map SHA `38d656d489d4b1a3c2880dbd3b0aebe2e7f9a316fe2e02902c62258d906a0548`)
and `DECODE_INDEX_TARGET.json` (map SHA
`536b2328655e77bd91cd71e2619309ef91768161cc0b4c6f62a318dc6dcad0ef`).

For each anchor, first create a fresh exact one-function static map using the
actual-owner V2 mapper.  Its map must explicitly carry `mref_count` and
`width_bytes`; the historical Route-A maps lack those fields and are not
silently promoted.  Freeze every `GLOBAL && has_mref` row and every MREF
ordinal with:

```bash
python3 util/vm_tlb/c16/lane_g/route_b_q2_bridge.py freeze \
  --anchor PREFILL --static-map "$RUN/prefill_exact_map.tsv" --code-object "$RUN/observed_owner.so" \
  --whitelist-json "$RUN/prefill_whitelist.json" --whitelist-tsv "$RUN/prefill_whitelist.tsv"
python3 util/vm_tlb/c16/lane_g/route_b_q2_bridge.py freeze \
  --anchor DECODE --static-map "$RUN/decode_exact_map.tsv" --code-object "$RUN/observed_owner.so" \
  --whitelist-json "$RUN/decode_whitelist.json" --whitelist-tsv "$RUN/decode_whitelist.tsv"
```

The result contains `(static_index,mref_ordinal)`, `mref_count`, exact static
map SHA, owner SHA, and whitelist SHA.  Any missing identity, width, MREF
count, mixed function, or empty all-GLOBAL set fails closed.

For the comparison, Lane A must supply a hash-closed
`C16_ROUTE_A_BRIDGE_REFERENCE_V1` from existing raw Route-A authority.  It
must name the exact function/static index, bucket shift, sorted per-instance
executing-lane cardinalities, and selected-PC address-bucket cardinality.  The
checker compares those structural quantities only; it intentionally never
requires absolute GPU VA equality across processes.  No such reference is
fabricated by this branch.  After the producer parser has closed the raw
stream, serialize its LANE_EVENT list and run:

```bash
python3 util/vm_tlb/c16/lane_g/route_b_q2_bridge.py check \
  --raw-events-json "$RUN/q2_lane_events.json" --route-a-reference "$RUN/route_a_reference.json"
```
