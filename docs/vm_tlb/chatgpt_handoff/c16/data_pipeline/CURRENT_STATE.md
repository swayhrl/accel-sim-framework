# C16 Data Pipeline — Current State

## Accepted handover anchors

Old174 final handover:

- branch: `hrl/c16-old174-final-handover-to-2239-v0`
- commit: `674e834d25ab4f5be914bcebe021ce685eb51e54`
- decision: `OLD174_HANDOVER_COMPLETE`
- old174 role after acceptance: `HISTORICAL_SOURCE_ONLY`

RTX4080 clean Llama baseline:

- branch: `hrl/c16-4080-u5-u9-r5-clean`
- commit: `b75f26674a09705659e770ab2134351414aa3c93`
- R5 is the accepted clean Llama qualification baseline;
- R4 quantitative data remains mechanism-only/non-authoritative.

## Frozen topology

```text
109 / RTX4080
  producer / GPU capture
        |
        | ssh hrl174new
        v
174-new / 2239
  ingest / verify / catalog / CPU analysis
        |
        v
164 through /root/share/mnt164
  long-term raw / provenance / parsed / features / datasets
```

Reverse control path:

```text
174-new -> ssh gpu109
```

No future pipeline should depend on old174 as a live runner.

## Old174 handover conclusions accepted

- 3090 Route-B Q1, Q2 Prefill, Q2 Decode and Route-A→Q2 bridge raw evidence is catalogued and hash-closed.
- A curated historical comparison subset is approximately 763.9 MB and is a future copy-not-move archive candidate.
- Route-B map remains 34/36 exact; two required CUTLASS rows stay `FAILED_CLOSED_CODE_OBJECT_IDENTITY_UNRESOLVED`; do not reinterpret or repair as part of the data-plane work.
- Qwen2.5-0.5B, Qwen2.5-7B raw and Qwen2.5-7B AWQ have 21 historical frozen scenario bindings catalogued.
- Qwen3-8B and DeepSeek-V2-Lite remain `NO_HISTORICAL_FROZEN_BINDING`.
- Qwen3-30B-A3B remains outside the accepted V0 authority; it needs a separately scoped manifest/input-binding closeout.
- No filesystem-only critical future code was found; Git remains the code authority.
- `/root/share/c16_recovery_v3` and `/workspace/c16_exchange/autodl_wave1` remain retained historical sources; do not bulk move/delete them.

## Important authority nuance

The old174 V2A/V2C historical/adopted-input distinction must not weaken or replace the already accepted RTX4080 R5 replay authority on node109.

For future archival/import of R5, node109's exact local R5 model/input/receipt/artifact closure is authoritative. Old174's historical missing-bundle result remains an archaeology fact only.

## Storage state

174-new local storage is unsuitable for large data:

- overlay and `/root/data`: effectively full;
- `/root/share`: highly utilized;
- `/root/share/mnt164`: ~72 TB free and is the intended long-term data plane.

The previous candidate root was:

`/root/share/mnt164/huangrulin/c16_ai_workload_2239`

This was only a planning/admission candidate and had no accepted scientific payload migration.

### Canonical root decision for Phase B

Use the port-independent canonical root:

`/root/share/mnt164/huangrulin/c16_ai_workload`

The `_2239` suffix is not part of scientific identity and is superseded before formal namespace creation. If either canonical or legacy candidate root already contains non-fixture data, fail closed and report; do not rename, merge or delete it without review.

## Immediate execution order

1. Phase B: new174/164 data-root admission and namespace freeze.
2. Review Phase B.
3. Phase C: pipeline V1 with synthetic fixtures: RUN_ID, manifest, finalize, transfer, verify, ACK, catalog.
4. Phase D: legacy RTX4080 R5 import from node109 after its provenance-only closeout is accepted.
5. Curated 3090 historical archive import when useful.
6. Multi-model capture through the new pipeline.
7. Analysis pipeline and cross-model datasets.

Do not skip Phase B/C and start ad-hoc large trace transfer.
