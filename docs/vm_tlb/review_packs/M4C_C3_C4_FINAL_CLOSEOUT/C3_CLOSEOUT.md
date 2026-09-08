# C3 8/8 terminal closeout

Every arm below passed its formal terminal gate: simulator exit status is zero,
the `Processing kernel` / started-kernel marker count equals its immutable
kernel-list entry count, and telemetry-kernel record count equals that same
count.  A marker count by itself is not completion proof.

| Arm | Result | Expected list entries | Processing-kernel markers | Telemetry records | Simulator exit |
| --- | --- | ---: | ---: | ---: | ---: |
| decode1-disabled | PASS | 740 | 740 | 740 | 0 |
| decode1-ideal | PASS | 740 | 740 | 740 | 0 |
| decode1-generic | PASS | 740 | 740 | 740 | 0 |
| decode1-paper | PASS | 740 | 740 | 740 | 0 |
| prefill-disabled | PASS | 692 | 692 | 692 | 0 |
| prefill-ideal | PASS | 692 | 692 | 692 | 0 |
| prefill-generic | PASS | 692 | 692 | 692 | 0 |
| prefill-paper | PASS | 692 | 692 | 692 | 0 |

The C4 validation table additionally records generic/paper PTE/requester/object
conservation, terminal quiescence, exporter provenance, and no-replay status.
Raw formal log identities are retained only in `RAW_LOG_INDEX.tsv` and
`INPUT_ARTIFACT_INDEX.tsv`.
