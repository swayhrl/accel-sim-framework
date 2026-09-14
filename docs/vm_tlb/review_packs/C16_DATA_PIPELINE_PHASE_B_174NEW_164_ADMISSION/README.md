# C16 data pipeline Phase B — 174-new / node164 admission

This review pack records **Phase B only**: admission and namespace freeze for
the long-term node164 data root reachable from 174-new through SSHFS. It
contains no GPU execution, no node109 access, no R5 import, no RTX3090 import,
and no scientific raw payload.

## Decision

`DATA_ROOT_ADMISSION_PASS`

The canonical root is frozen as:

```text
/root/share/mnt164/huangrulin/c16_ai_workload
```

The previous port-labelled candidate
`/root/share/mnt164/huangrulin/c16_ai_workload_2239` was observed absent and
was not created, renamed, merged, or removed. Before creation, the canonical
root was also absent. The namespace is empty apart from the frozen directory
layout and the catalog schema seed installed at `catalog/CATALOG_SCHEMA_V1.json`.

## Evidence

- `DATA_ROOT_ADMISSION_V1.json` records mount capacity, namespace and fixture
  results.
- `FILESYSTEM_SEMANTICS.json` records observed SSHFS semantics.
- `CATALOG_SCHEMA_V1.json` defines the empty catalog entry schema.
- `PHASE_B_DECISION.json` is the scope/decision receipt.
- `SHA256SUMS` closes this review pack.

All fixture data was deterministic and synthetic. The small and 64 MiB
fixtures were written directly to the admitted root, re-opened and hashed,
renamed within the root, then fully removed.

## Next boundary

Phase C requires review authorization. It may implement the synthetic-fixture
transfer lifecycle only; this Phase B result does not authorize transfer of
scientific evidence.
