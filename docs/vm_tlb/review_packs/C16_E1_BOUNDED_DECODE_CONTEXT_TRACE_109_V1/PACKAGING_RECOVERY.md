# Packaging-root recovery

The initial Pipeline dry-run used the transfer-compatible path `c16_ai_workload/captures/inbox/<RUN_ID>.partial`. Independent SHA verification there passed, but Pipeline V1 admission correctly failed without mutation because that compatibility subtree has no `raw/` or `catalog/` parents.

State audit proved:

- the partial bundle remained present and unchanged;
- no raw object, catalog entry or ACK had been created;
- manifest SHA remained `db3bdbb0295a47a6aa4644508ea1895779c987f2f77cd96f184c67b8a10ab389`.

The verified partial directory was moved with non-overwrite same-mount rename into the canonical Pipeline V1 root:

`/root/share/mnt164/huangrulin/c16_ai_workload/inbox/<RUN_ID>.partial`

The accepted 174-new consumer then re-ran full independent verification from the canonical root before admission. Canonical verification, raw promotion, catalog creation and positive ACK all passed. The earlier compatibility-root verification receipt is diagnostic provenance only and is not the admission authority.
