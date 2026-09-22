# V40 current status for review

## Closed engineering evidence

- V40 deterministic supervisor owns every target with `Popen(...,
  start_new_session=True)`, persists M0–M6 markers, captures timeout diagnostics,
  and terminates the process group on timeout.
- Official NVBit 1.7.7.1 `mem_trace` on the exact isolated actual-A expert58
  replay reached M0–M6 and exited `rc=0` after the marker's BF16 raw-bit hash was
  repaired.  This is the `CLEAN_DYNAMIC_PATH` control.
- Official-derived P1/P2/P3/P4/P5 work roots were created under
  `/data/c16/tools/v40_p*_...`; P5 has no device-side sequence-order spin.
- P5 vector controls were run for a nonzero static and a valid zero static, and
  the independent accounting validator was exercised with a count corruption.

## Current sweep evidence

`/data/c16/olmoe_v40/typed_sweep/TYPED_SWEEP.json` is append-only/restartable.
Each completed attempt has an individual supervisor root under
`/data/c16/olmoe_v40/supervised/static_<index>/`, containing supervisor receipt,
durable markers, output hash, and—only after a clean P5 replay—same-process
`ADDRESS_CONTEXT.json` and trace.

The sweep has processed multiple selector rows.  Some attempts lack an address
context/output hash and are retained as failed/excluded attempts, not canaries.
The review question still open is whether the accepted clean attempts contain
all three required typed roles (`EXPERT_DOWN_INPUT`, `EXPERT_DOWN_WEIGHT`, and
`EXPERT_DOWN_OUTPUT`).  Until that receipt says all three are present, no formal
243-shard run, admission, ACK, or handoff is claimed.

## Not closed

- typed canary role set;
- P5 source/receiver serializer review-pack closure;
- complete 243-shard formal capture and executed/zero partition;
- formal analysis, admission, positive ACK, and third-lineage handoff.

No incomplete trace or failed supervisor attempt has been admitted as formal
scientific evidence.
