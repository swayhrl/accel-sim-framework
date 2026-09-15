# Discussion Reference — Why This Inheritance Exists

## User concern

The current 174-new analysis node has already inherited the modern C16 raw-trace / parser / fingerprint pipeline, but it is unclear whether the older TLB/Cache simulation framework, historical simulator run outputs, and C12–C15 result assets have been formally inherited.

The old and new 174 Docker containers are reached through different SSH ports on the same host:

```text
old174: root@10.208.130.174:2233
new174: root@10.208.130.174:2239
```

The administrator mapped `/root/share` and `/root/data` from both containers to the same host-backed storage. Therefore some historical assets may already be visible to both containers, while other old run outputs may live only in the old container-private overlay.

## Why we cannot simply let 174-new search blindly

The historical work has several layers that must not be conflated:

1. **Git code/config authority** — source, configs, analyzers and documents that already have versioned provenance;
2. **shared filesystem artifacts** — traces/results physically visible to both containers;
3. **old-container-private artifacts** — potentially irreplaceable run outputs that would disappear when 2233 is retired;
4. **historical claims** — conclusions that are only trustworthy if tied back to exact inputs/configs/code/output.

A blind `find` on 174-new cannot prove whether an absent artifact never existed or exists only in the old container-private layer.

## Scientific reason to preserve the lineage

Current C16 work is producing new model-native memory evidence. Future research needs to compare those observations with the older simulation-based TLB/Cache work rather than create a disconnected second analysis stack.

The desired long-term structure is:

```text
174-new
├── native characterization
│   ├── C16WARP1 / formal raw ingest
│   ├── page/cache-line fingerprints
│   └── object/KV/weight attribution
│
└── simulator characterization
    ├── historical C12–C15 baselines
    ├── TLB/PTW analysis
    ├── Segment / Selective analysis
    ├── Cache analysis
    └── future replay of selected new traces
```

The inheritance is therefore not archival housekeeping. It is required to preserve continuity between historical simulation conclusions and the current multi-model characterization program.

## Why Round 1 is inventory-only

Large historical trees may already be shared-mounted. Copying first and understanding later would:

- duplicate data unnecessarily;
- obscure which copy was historically authoritative;
- risk mixing old simulation raw with current Pipeline formal captures;
- make eventual cleanup unsafe.

Therefore Round 1 reconstructs provenance and visibility first. Round 2 migrates only what truly needs migration.

## Expected Round-2 actions after joint review

Depending on evidence, ChatGPT will authorize some subset of:

- copy-not-move of `OLD_DOCKER_PRIVATE_MUST_MIGRATE` assets to node164;
- destination rehash and archive receipt creation;
- shared-path visibility closure from 174-new;
- trace/config/run/result lineage catalog creation;
- a small number of historical anchor replays to prove current compatibility;
- current simulator-wrapper repairs if historical interfaces no longer run;
- a formal bridge from current C16-derived data to historical TLB/Cache analysis where scientifically valid.

Round 2 will not rerun all historical experiments by default.
