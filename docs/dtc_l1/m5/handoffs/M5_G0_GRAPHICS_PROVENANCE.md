# M5 G0 Graphics Provenance

Status: source-backed provenance recovered; no simulator-execution claim.

Canonical audit source: `https://github.com/glmark2/glmark2`, commit
`22c527cb0556f3a1ac4445aaa52cc532760928d5`, cloned at
`/tmp/dtc-l1-m5-glmark2` for this audit.  glmark2 is the closest currently
source-backed release; the thesis reference/version is not pinned in the
available handoff material.

| Thesis label | Current source-backed scene / invocation candidate | Assets and fidelity finding |
| --- | --- | --- |
| jellyfish | `jellyfish --size 800x600` | `data/models/jellyfish.jobj` SHA `5004c52d8b834521a30929f778bee211330f80ee7e22ef3401be7893688bebc2`; `data/textures/jellyfish256.png` SHA `f22ee4c18b6d2be25e0025c3292f7f94fe3677881c0b6f045c84416cf961fc31`; shaders `jellyfish.vert` / `.frag`. Current source additionally cycles 32 caustic textures, so the thesis `2 x 256 x 256` notation is not assumed identical. |
| cat-tex | `texture:model=cat:texture=crate-base --size 800x600` | `data/models/cat.3ds` SHA `9e535473afd73d3dbeda82e98f32072853cf2966048f69613739813fa4695450`; `data/textures/crate-base.png` is 512x512, SHA `bf76ecdbab16091fbe63581cf209baf9cb3b8921f94da84b42689c43c6c02102`; shaders `light-basic.vert` / `light-basic-tex.frag`. Source-backed candidate, not a claim that current mesh vertex count is the thesis count. |
| cube-tex | `texture:model=cube:texture=crate-base --size 800x600` | `data/models/cube.3ds` SHA `8d8b716db79445dbd009da40b788b6c3cd4760035ed17f5dd9b53d1050c799b9`; same 512x512 crate texture and shaders. Source-backed candidate. |
| 2D-tex | unresolved exact mapping | Current `effect2d` uses four grid vertices but `effect-2d.png` is 800x600 (SHA `d4c20048e4c73ca9935751cc44153c8c0ef0a4382c96be900d5219dcfc7d7145`), not the thesis 128x128 asset / 256x256 resolution. It is therefore not silently substituted. |
| horse | `build:model=horse --size 800x600` | `data/models/horse.3ds` SHA `1c241dbf9188b5c673cb6d1887492e305d53eba5ccf194e90314d8deb9d0a111`; source scene defaults to model `horse` and does not select a texture. Source-backed candidate, with thesis vertex count still to be version-resolved. |

All candidates require the normal glmark2 flavor/window-system invocation in
addition to the scene string.  Asset and version discrepancies remain visible;
none has been converted to a compute workload or a simulator result.
